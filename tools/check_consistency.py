#!/usr/bin/env python3
"""Consistency checks for the htn-research repository.

Checks:
  1. every HTN-xx ID in FINDINGS.md has findings/HTN-xx.md and vice versa;
  2. every finding file has all required sections, in order;
  3. the metadata row in each finding file agrees with its FINDINGS.md row (severity, category, evidence, chain
     impact, action);
  4. key numbers appear where expected and no conflicting variant appears anywhere;
  5. body word count per finding is within 150-400 words (metadata table, Upstream section and fixed boilerplate
     excluded);
  6. every Verification section carries both the 'Completed' and the 'Required before submission' labels;
  7. the withdrawn test-end time does not reappear;
  8. every figure listed in FIGURES exists, is well-formed XML with <title>/<desc>, contains the expected values in its
     text, those values also appear in the source report, every Markdown image link resolves to a file, and every SVG
     under figures/ is listed in figures/README.md.

Exit code 0 when everything passes, 1 otherwise. Standard library only.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FINDINGS_MD = os.path.join(ROOT, "FINDINGS.md")
FINDINGS_DIR = os.path.join(ROOT, "findings")

README_MAX_WORDS = 1500
README_MAX_BULLETS = {"What is better now": 10, "What we are working on": 12}

SECTIONS = ["Summary", "Affected code", "Impact", "Evidence", "Recommendation", "Verification",
            "Chain impact", "Related items", "Upstream"]

# (pattern, files that must contain it, forbidden variants that must appear nowhere)
KEY_NUMBERS = [
    (r"101/183", ["FINDINGS.md", "README.md", "METHODOLOGY.md", "findings/HTN-01.md"],
     [r"\b101 of 183\b", r"\b102/183\b", r"\b100/183\b"]),
    (r"342\.9 MB", ["README.md", "findings/HTN-08.md", "reports/memory-test.md"],
     [r"\b343 MB\b(?! per node)", r"342,9", r"\b342\.9 MiB\b"]),
    (r"8\.792 ?% to 1\.120 ?%", ["findings/HTN-04.md", "reports/red-blocks.md"],
     [r"8\.79 ?%", r"1\.12 ?%(?! \()", r"8,792", r"1,120 ?%"]),
    (r"9\.622 ?% to 0\.590 ?%", ["findings/HTN-04.md", "reports/red-blocks.md"],
     [r"9\.62 ?%", r"0\.59 ?%", r"9,622", r"0,590"]),
]

WORD_MIN, WORD_MAX = 150, 400

# allowed status prefixes in the metadata row (review outcomes are appended in parentheses)
STATUSES = ("Draft — not yet submitted", "Draft — changes requested in review", "Draft — rework required",
            "Prototype — not ready", "Submitted", "Merged", "Closed", "Rejected", "Reported privately")

# figure file -> (labels that must appear in the SVG text, source report, values that must appear in that report)
FIGURES = {
    "red-blocks-by-k.svg": (["8.792", "11.041", "4.533", "2.220", "1.630", "1.120", "0.816"], "reports/red-blocks.md",
                            ["8.792", "11.041", "4.533", "2.220", "1.630", "1.120", "0.816"]),
    "pow-fma-arm64.svg": (["82", "101", "183"], "findings/HTN-01.md", ["101/183", "183/183"]),
    "memory-budget.svg": (["8.00 GB", "2.15 GB", "0.40 GB", "8 GB host RAM"], "findings/HTN-17.md",
                          ["8 GB", "2 GiB", "384 MiB", "256/128 MiB"]),
    "parent-count-distribution.svg": (["23.7", "35.1", "25.5", "11.2", "4.5"], "reports/red-blocks.md",
                                      ["23.7 %", "35.1 %", "25.5 %", "11.2 %", "4.5 %"]),
    "pp-move-cascade.svg": (["+107.9 s", "+108.1 s", "+125 s", "+351 s", "+315 s", "243 s", "207 s", "380 s", "317 s"],
                            "findings/HTN-39.md", ["+107.9 s", "+108.1 s", "243 s (A) and 207 s (B)"]),
    "gbt-cache-before-after.svg": (["46.7 %", "8.5 %", "32.2 %", "0.18 %", "2.07 %", "0.95 %", "8.05 %", "6.78 %"],
                                   "findings/HTN-44.md", ["46.7 %", "8.5 %", "32.2 %", "0.18 %", "2.07 %", "0.95 %",
                                                          "8.05 %", "6.78 %", "+0.15 pp"]),
    "memory-timeline.svg": (["7 GiB cap", "OOM kill (process restarted)", "node A (with UTXO index)",
                             "node B (without UTXO index)", "hours since the start of phase A"], "reports/memory-test.md",
                            ["6.18 / 6.84 / 7.55", "5.70 / 6.44 / 7.50", "6.12 / 6.85 / 6.98", "5.79 / 6.52 / 6.95",
                             "OOM kills"]),
}

errors = []
warnings = []


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def all_md_files():
    out = []
    for dirpath, _, files in os.walk(ROOT):
        for f in files:
            if f.endswith(".md"):
                out.append(os.path.join(dirpath, f))
    return sorted(out)


# ---- 1. IDs <-> files
findings_text = read(FINDINGS_MD)
table_rows = [l for l in findings_text.splitlines() if l.startswith("| [HTN-")]
table_ids = [re.match(r"\| \[(HTN-\d\d)\]", l).group(1) for l in table_rows]
file_ids = sorted(f[:-3] for f in os.listdir(FINDINGS_DIR) if re.fullmatch(r"HTN-\d\d\.md", f))

for i in table_ids:
    if i not in file_ids:
        errors.append(f"{i} is in FINDINGS.md but findings/{i}.md is missing")
for i in file_ids:
    if i not in table_ids:
        errors.append(f"findings/{i}.md exists but {i} is not in FINDINGS.md")
if len(table_ids) != len(set(table_ids)):
    errors.append("duplicate IDs in FINDINGS.md")
if table_ids != sorted(table_ids):
    warnings.append("FINDINGS.md rows are not in ID order")

# parse table rows into dicts
table_meta = {}
for l in table_rows:
    cells = [c.strip() for c in l.strip().strip("|").split("|")]
    # ID | Title | Severity | Category | Evidence | Chain impact | Action | Status | Upstream
    if len(cells) != 9:
        errors.append(f"FINDINGS.md row has {len(cells)} cells, expected 9: {l[:60]}")
        continue
    fid = re.match(r"\[(HTN-\d\d)\]", cells[0]).group(1)
    table_meta[fid] = dict(sev=cells[2], cat=cells[3], ev=cells[4], chain=cells[5], action=cells[6],
                           status=cells[7], upstream=cells[8])

# ---- 2 + 3 + 5. per-file checks
for fid in file_ids:
    path = os.path.join(FINDINGS_DIR, fid + ".md")
    text = read(path)
    heads = re.findall(r"^## (.+)$", text, flags=re.M)
    if heads != SECTIONS:
        missing = [s for s in SECTIONS if s not in heads]
        extra = [h for h in heads if h not in SECTIONS]
        errors.append(f"{fid}: sections mismatch (missing {missing}, extra {extra}, order ok={heads == [h for h in SECTIONS if h in heads]})")
    if not text.startswith(f"# {fid} — "):
        errors.append(f"{fid}: title line does not start with '# {fid} — '")
    m = re.search(r"^\| (High|Medium|Low|Informational|Critical) \| (.+?) \| (.+?) \| (.+?) \| (PR|Issue) \| (.+?) \| (.+?) \|$", text, flags=re.M)
    if not m:
        errors.append(f"{fid}: metadata row not found or malformed")
    elif fid in table_meta:
        sev, cat, ev, chain, action, status, upstream = m.groups()
        t = table_meta[fid]
        for name, a, b in [("severity", sev, t["sev"]), ("category", cat, t["cat"]), ("evidence", ev, t["ev"]),
                           ("chain impact", chain, t["chain"]), ("action", action, t["action"]),
                           ("status", status, t["status"]), ("upstream", upstream, t["upstream"])]:
            if a != b:
                errors.append(f"{fid}: {name} differs (file '{a}' vs FINDINGS.md '{b}')")
    if not any(st in text for st in STATUSES):
        errors.append(f"{fid}: no known status ({', '.join(STATUSES)})")
    if not re.search(r"^## Upstream\n\n(TBD|PR \[|Issue \[)", text, flags=re.M):
        errors.append(f"{fid}: Upstream section must start with TBD or a PR/issue link")
    ver = re.search(r"^## Verification\n(.*?)^## Chain impact", text, flags=re.M | re.S)
    if not ver or "**Completed:**" not in ver.group(1) or "**Required before submission:**" not in ver.group(1):
        errors.append(f"{fid}: Verification must contain both 'Completed' and 'Required before submission' labels")
    if re.search(r"\b16:00\b", text):
        errors.append(f"{fid}: contains the removed test-end time")
    # related links resolve
    for rel in re.findall(r"\[(HTN-\d\d)\]\((HTN-\d\d)\.md\)", text):
        if rel[0] != rel[1]:
            errors.append(f"{fid}: related link text/target mismatch {rel}")
        if rel[1] not in file_ids:
            errors.append(f"{fid}: related item {rel[1]} has no file")
    # body word count: drop title, metadata table, headings, diagrams, images and fixed boilerplate
    body = re.sub(r"```mermaid.*?```", "", text, flags=re.S)
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", body)
    body = re.sub(r"^## Upstream\n.*?(?=^## |^_AI disclosure|\Z)", "", body, flags=re.M | re.S)
    body = re.sub(r"^# .*$", "", body, flags=re.M)
    body = re.sub(r"^\|.*\|$", "", body, flags=re.M)
    body = re.sub(r"^## .*$", "", body, flags=re.M)
    body = body.replace("Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.", "")
    body = body.replace("TBD — PR/issue link to be filled in once submitted.", "")
    body = body.replace("_AI disclosure: prepared with AI assistance (Claude by Anthropic; cross-reviewed with OpenAI Codex)._", "")
    words = len(body.split())
    if words < WORD_MIN or words > WORD_MAX:
        errors.append(f"{fid}: body has {words} words (allowed {WORD_MIN}-{WORD_MAX})")

# ---- 4. key numbers
md_files = all_md_files()
corpus = {os.path.relpath(p, ROOT): read(p) for p in md_files}
for f, txt in corpus.items():
    if re.search(r"\b16:00\b", txt):
        errors.append(f"{f}: contains the removed test-end time")
for pattern, must_have, forbidden in KEY_NUMBERS:
    rx = re.compile(pattern)
    for f in must_have:
        if f not in corpus:
            errors.append(f"key number {pattern!r}: expected file {f} missing")
        elif not rx.search(corpus[f]):
            errors.append(f"key number {pattern!r} not found in {f}")
    for frx in forbidden:
        for f, txt in corpus.items():
            for mm in re.finditer(frx, txt):
                errors.append(f"conflicting variant {frx!r} in {f}: '{txt[max(0, mm.start()-30):mm.end()+30].strip()}'")

# ---- 8. figures
import xml.dom.minidom
FIG_DIR = os.path.join(ROOT, "figures")
fig_readme = read(os.path.join(FIG_DIR, "README.md")) if os.path.exists(os.path.join(FIG_DIR, "README.md")) else ""
for name, (values, source, source_values) in FIGURES.items():
    path = os.path.join(FIG_DIR, name)
    if not os.path.exists(path):
        errors.append(f"figure missing: figures/{name}")
        continue
    try:
        dom = xml.dom.minidom.parse(path)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"figures/{name}: not well-formed XML ({exc})")
        continue
    if not dom.getElementsByTagName("title") or not dom.getElementsByTagName("desc"):
        errors.append(f"figures/{name}: missing <title> or <desc>")
    svg_text = " ".join(n.firstChild.data for n in dom.getElementsByTagName("text") if n.firstChild)
    src = corpus.get(source, "")
    for v in values:
        if v not in svg_text:
            errors.append(f"figures/{name}: label {v!r} not in SVG text")
    for v in source_values:
        if v not in src:
            errors.append(f"figures/{name}: source value {v!r} not found in {source}")
    if f"`{name}`" not in fig_readme:
        errors.append(f"figures/{name} is not listed in figures/README.md")
for f in sorted(os.listdir(FIG_DIR)) if os.path.isdir(FIG_DIR) else []:
    if f.endswith(".svg") and f not in FIGURES:
        errors.append(f"figures/{f} exists but is not registered in FIGURES / checked")
for f, txt in corpus.items():
    for alt, target in re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", txt):
        tpath = os.path.normpath(os.path.join(ROOT, os.path.dirname(f), target))
        if not os.path.exists(tpath):
            errors.append(f"{f}: image link {target} does not resolve")
        if not alt.strip():
            errors.append(f"{f}: image {target} has empty alt text")

# ---- the front page stays short (owner 2026-10-17): the latest release only, a capped work list, a word budget.
# Older releases live in CHANGES.md "By release" (generated daily from GitHub).
readme = read(os.path.join(ROOT, "README.md"))
visible = re.sub(r"\]\([^)]*\)", "]", re.sub(r"<details>.*?</details>", "", readme, flags=re.S))
if len(visible.split()) > README_MAX_WORDS:
    errors.append(f"README.md: {len(visible.split())} visible words (max {README_MAX_WORDS}); move detail to CHANGES.md")
for head, cap in README_MAX_BULLETS.items():
    sec = re.search(rf"^## {head}\n(.*?)(?=^## )", readme, re.M | re.S)
    n = len(re.findall(r"^- ", sec.group(1), re.M)) if sec else -1
    if not 0 < n <= cap:
        errors.append(f"README.md: section '{head}' has {n} items (1..{cap}); keep only the latest release / main work")

# ---- summary
sev_counts = {}
for t in table_meta.values():
    sev_counts[t["sev"]] = sev_counts.get(t["sev"], 0) + 1

print(f"findings in table: {len(table_ids)}, files: {len(file_ids)}")
print("severity counts: " + ", ".join(f"{k} {v}" for k, v in sorted(sev_counts.items(), key=lambda kv: ['High', 'Medium', 'Low', 'Informational'].index(kv[0]) if kv[0] in ['High', 'Medium', 'Low', 'Informational'] else 99)))
for w in warnings:
    print("WARN:", w)
for e in errors:
    print("ERROR:", e)
print("RESULT:", "PASS" if not errors else f"FAIL ({len(errors)} errors)")
sys.exit(0 if not errors else 1)
