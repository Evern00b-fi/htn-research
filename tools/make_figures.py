#!/usr/bin/env python3
"""Generate the standalone SVG figures under figures/.

Run from anywhere: python3 tools/make_figures.py
The first four figures use the standard library only. The figures added later (pruning-point move, bridge template
cache) use matplotlib and also write a PNG preview; they are skipped with a note when matplotlib is not installed.
Numbers are taken from reports/red-blocks.md (R1, R2, R3), reports/memory-test.md and findings/HTN-01, -17, -39, -40,
-44; each matplotlib figure asserts that its numbers appear in its source text, and the consistency checker
(tools/check_consistency.py) verifies that the values embedded in the SVG text match those reports.
"""
import os
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "figures")

# Okabe-Ito colour-blind-safe palette
ORANGE, SKY, GREEN, YELLOW, BLUE, VERMILION, PURPLE, BLACK = (
    "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7", "#000000")
FONT = "font-family=\"Helvetica, Arial, sans-serif\""

W = 700  # all figures are 700 px wide


class SVG:
    def __init__(self, h, title, desc):
        self.h = h
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" '
            f'aria-labelledby="t d">',
            f'<title id="t">{escape(title)}</title>',
            f'<desc id="d">{escape(desc)}</desc>',
            f'<rect width="{W}" height="{h}" fill="#ffffff"/>']

    def text(self, x, y, s, size=13, anchor="start", weight="normal", fill=BLACK, rotate=None):
        tr = f' transform="rotate(-90 {x} {y})"' if rotate else ""
        self.parts.append(f'<text x="{x}" y="{y}" {FONT} font-size="{size}" text-anchor="{anchor}" '
                          f'font-weight="{weight}" fill="{fill}"{tr}>{escape(s)}</text>')

    def rect(self, x, y, w, h, fill, stroke="none"):
        self.parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" stroke="{stroke}"/>')

    def line(self, x1, y1, x2, y2, stroke=BLACK, width=1, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{width}"{d}/>')

    def save(self, name):
        self.parts.append("</svg>")
        os.makedirs(OUT, exist_ok=True)
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
            fh.write("\n".join(self.parts) + "\n")
        print("wrote", os.path.relpath(os.path.join(OUT, name), ROOT))


def axes(svg, left, top, right, bottom, ymax, ystep, ylabel, yfmt):
    """Draw a y axis with gridlines; return a function mapping a value to a pixel y."""
    scale = (bottom - top) / ymax

    def y(v):
        return bottom - v * scale

    svg.line(left, top, left, bottom)
    svg.line(left, bottom, right, bottom)
    v = 0
    while v <= ymax + 1e-9:
        svg.line(left, y(v), right, y(v), stroke="#dddddd")
        svg.text(left - 8, y(v) + 4, yfmt(v), size=12, anchor="end")
        v += ystep
    svg.text(18, (top + bottom) / 2, ylabel, size=13, anchor="middle", rotate=True)
    return y


def caption(svg, lines, y0, size=11):
    for i, l in enumerate(lines):
        svg.text(W / 2, y0 + i * (size + 4), l, size=size, anchor="middle", fill="#333333")


# ---------------------------------------------------------------- (a) red share by K rule
def fig_red_blocks():
    data = [("parents (today)", 8.792), ("K=3", 11.041), ("K=5", 4.533), ("K=8", 2.220),
            ("K=11", 1.630), ("K=18", 1.120), ("K=40", 0.816)]
    svg = SVG(430, "Red share of all blocks per K rule (R2 counterfactual re-colouring)",
              "Bar chart. Red share of all blocks when the recorded mainnet DAG is re-coloured under different "
              "GHOSTDAG K rules: parents (today) 8.792 %, K=3 11.041 %, K=5 4.533 %, K=8 2.220 %, K=11 1.630 %, "
              "K=18 1.120 %, K=40 0.816 %. Frozen topology; full-window variants exceed the 180-block merge-set limit.")
    svg.text(W / 2, 28, "Red share of all blocks per K rule (R2, same recorded DAG)", size=16, anchor="middle", weight="bold")
    left, top, right, bottom = 70, 50, 670, 320
    y = axes(svg, left, top, right, bottom, 12, 2, "red share of all blocks (%)", lambda v: f"{v:.0f} %")
    n = len(data)
    slot = (right - left) / n
    bw = slot * 0.6
    for i, (label, v) in enumerate(data):
        x = left + i * slot + (slot - bw) / 2
        fill = VERMILION if i == 0 else BLUE
        svg.rect(x, y(v), bw, bottom - y(v), fill)
        svg.text(x + bw / 2, y(v) - 6, f"{v:.3f} %", size=12, anchor="middle", weight="bold")
        svg.text(x + bw / 2, bottom + 18, label, size=12, anchor="middle")
    svg.text(W / 2, bottom + 40, "K rule applied in the replay", size=13, anchor="middle")
    caption(svg, ["Frozen topology: parents, templates and difficulty are kept as recorded. Full-window variants contain",
                  "merge sets above the 180-block limit (11 at K=18) and are not executable histories; a limit-consistent",
                  "prefix gives 9.622 % to 0.590 % at K=18. Not a prediction of live red rates. Source: reports/red-blocks.md."],
            bottom + 66)
    svg.save("red-blocks-by-k.svg")


# ---------------------------------------------------------------- (b) PoW validity by build
def fig_pow_fma():
    groups = [("darwin/arm64, unpatched", 82, 101), ("amd64 v1", 183, 0), ("darwin/arm64, patched", 183, 0)]
    svg = SVG(400, "Hoohash v1.1.0 PoW validity of 183 real mainnet blocks by build",
              "Grouped bar chart. Valid and invalid PoW verdicts for 183 consecutive real mainnet blocks: darwin/arm64 "
              "unpatched build 82 valid, 101 invalid; amd64 v1 build 183 valid, 0 invalid; darwin/arm64 patched build "
              "183 valid, 0 invalid. Tested sample of 183 real mainnet blocks.")
    svg.text(W / 2, 28, "PoW verdict on 183 real mainnet blocks, by build (HTN-01)", size=16, anchor="middle", weight="bold")
    left, top, right, bottom = 70, 50, 670, 300
    y = axes(svg, left, top, right, bottom, 200, 50, "blocks", lambda v: f"{v:.0f}")
    n = len(groups)
    slot = (right - left) / n
    bw = slot * 0.28
    for i, (label, valid, invalid) in enumerate(groups):
        cx = left + i * slot + slot / 2
        for j, (v, fill, name) in enumerate([(valid, GREEN, "valid"), (invalid, VERMILION, "invalid")]):
            x = cx - bw - 4 + j * (bw + 8)
            if v > 0:
                svg.rect(x, y(v), bw, bottom - y(v), fill)
            svg.text(x + bw / 2, y(v) - 6, f"{v}", size=12, anchor="middle", weight="bold")
            svg.text(x + bw / 2, bottom + 16, name, size=11, anchor="middle", fill="#444444")
        svg.text(cx, bottom + 34, label, size=12, anchor="middle")
    # legend
    svg.rect(left + 10, top + 6, 12, 12, GREEN); svg.text(left + 28, top + 16, "PoW valid", size=12)
    svg.rect(left + 110, top + 6, 12, 12, VERMILION); svg.text(left + 128, top + 16, "PoW invalid", size=12)
    caption(svg, ["Tested sample of 183 real mainnet blocks (header v10, all network-accepted). The unpatched arm64 build",
                  "rejects 101/183 because the compiler fuses multiply-add; the patch adds explicit float64() conversions.",
                  "Sampled agreement on amd64 is not a proof; the golden-vector test is the gate. Source: findings/HTN-01.md."],
            bottom + 56)
    svg.save("pow-fma-arm64.svg")


# ---------------------------------------------------------------- (c) memory budget
def fig_memory_budget():
    segs = [("Go soft limit (GOMEMLIMIT default)", 8.0, BLUE),
            ("Pebble block cache, 2 GiB (cgo, outside the Go limit)", 2.15, ORANGE),
            ("Serialized off-heap caches, 256 + 128 MiB", 0.40, GREEN)]
    svg = SVG(420, "Configured default memory budgets of HTND 2.18.1 versus an 8 GB host",
              "Stacked bar chart. Configured default budgets: Go soft limit 8.0 GB, Pebble cache 2 GiB (about 2.15 GB), "
              "serialized off-heap caches 256 plus 128 MiB (about 0.40 GB), total about 10.55 GB, against a horizontal "
              "line at 8 GB host RAM. These are configured budgets, not measured simultaneous occupancy.")
    svg.text(W / 2, 28, "Configured default memory budgets vs an 8 GB host (HTN-17)", size=16, anchor="middle", weight="bold")
    left, top, right, bottom = 70, 50, 400, 330
    y = axes(svg, left, top, right, bottom, 12, 2, "GB (decimal)", lambda v: f"{v:.0f}")
    bx, bw = 150, 160
    acc = 0.0
    for label, v, fill in segs:
        y1, y0 = y(acc), y(acc + v)
        svg.rect(bx, y0, bw, y1 - y0, fill)
        txt_fill = "#ffffff" if fill == BLUE else BLACK
        if y1 - y0 > 16:
            svg.text(bx + bw / 2, (y0 + y1) / 2 + 4, f"{v:.2f} GB", size=12, anchor="middle", weight="bold", fill=txt_fill)
        else:
            svg.text(bx + bw + 6, (y0 + y1) / 2 + 4, f"{v:.2f} GB", size=12, weight="bold")
        acc += v
    svg.text(bx + bw / 2, y(acc) - 8, f"total {acc:.2f} GB", size=13, anchor="middle", weight="bold")
    svg.line(left, y(8.0), right, y(8.0), stroke=VERMILION, width=2, dash="6,4")
    # right of the bar, so the label never overlaps the stacked segments
    svg.text(bx + bw + 8, y(8.0) - 6, "8 GB host RAM", size=11, fill=VERMILION, weight="bold")
    svg.text(bx + bw / 2, bottom + 18, "default configuration", size=12, anchor="middle")
    # legend on the right
    lx, ly = 430, 90
    for i, (label, v, fill) in enumerate(segs):
        svg.rect(lx, ly + i * 44, 14, 14, fill)
        words = label.split(", ")
        svg.text(lx + 22, ly + i * 44 + 12, words[0], size=12)
        if len(words) > 1:
            svg.text(lx + 22, ly + i * 44 + 28, ", ".join(words[1:]), size=11, fill="#444444")
    caption(svg, ["Configured budgets, not measured simultaneous occupancy: the Go runtime may stay well below its soft limit",
                  "and the caches fill over time. Measured occupancy is pending (reports/memory-test.md). Source: findings/HTN-17.md."],
            bottom + 44)
    svg.save("memory-budget.svg")


# ---------------------------------------------------------------- (d) parent-count distribution
def fig_parent_count():
    data = [("1", 23.7), ("2", 35.1), ("3", 25.5), ("4", 11.2), ("5+", 4.5)]
    svg = SVG(380, "Dynamic K = number of parents: distribution over 165,427 mainnet blocks (R1)",
              "Bar chart. Share of mainnet blocks by number of parents, which equals the GHOSTDAG K applied to the block: "
              "1 parent 23.7 %, 2 parents 35.1 %, 3 parents 25.5 %, 4 parents 11.2 %, 5 or more parents 4.5 %. "
              "165,427 blocks over about 9 hours, one node's view.")
    svg.text(W / 2, 28, "Dynamic K = number of parents (R1, 165,427 mainnet blocks)", size=16, anchor="middle", weight="bold")
    left, top, right, bottom = 70, 50, 670, 280
    y = axes(svg, left, top, right, bottom, 40, 10, "share of blocks (%)", lambda v: f"{v:.0f} %")
    n = len(data)
    slot = (right - left) / n
    bw = slot * 0.6
    for i, (label, v) in enumerate(data):
        x = left + i * slot + (slot - bw) / 2
        svg.rect(x, y(v), bw, bottom - y(v), SKY)
        svg.text(x + bw / 2, y(v) - 6, f"{v:.1f} %", size=12, anchor="middle", weight="bold")
        svg.text(x + bw / 2, bottom + 18, label, size=12, anchor="middle")
    svg.text(W / 2, bottom + 40, "number of parents = K used to colour the block", size=13, anchor="middle")
    caption(svg, ["K equals the number of direct parents the producer chose (1-12, MaxBlockParents). About 84 % of blocks are",
                  "coloured with K <= 3, which covers roughly 82 ms of delay at delta = 0.01. Source: reports/red-blocks.md (R1)."],
            bottom + 62)
    svg.save("parent-count-distribution.svg")


# ================================================================ matplotlib figures (added later)
# Same conventions as above: 700 px wide, Helvetica/Arial, Okabe-Ito palette, white background, bold 16 px title,
# 13 px axis labels, 12 px ticks, 11 px grey caption. Matplotlib works in points; the SVG is 525 pt = 700 px wide, so
# sizes below are px * 0.75.
PX = 0.75
GREY_LIGHT = "#BBBBBB"


def _src(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def _require(rel, *needles):
    text = _src(rel)
    for n in needles:
        assert n in text, f"{rel} does not contain {n!r}; figure data and text disagree"


def _wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * (p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5 / d
    return p, c - h, c + h


def _mpl():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 12 * PX, "axes.titlesize": 13 * PX, "axes.labelsize": 13 * PX,
        "xtick.labelsize": 12 * PX, "ytick.labelsize": 12 * PX, "legend.fontsize": 12 * PX,
        "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": BLACK, "axes.linewidth": 0.75,
        "axes.grid": True, "grid.color": "#dddddd", "grid.linewidth": 0.75, "axes.axisbelow": True,
        "svg.fonttype": "none", "svg.hashsalt": "htn-research", "figure.facecolor": "white",
    })
    return plt


def _save(fig, name, title, desc):
    """Write SVG (with <title>/<desc> for screen readers, no timestamp) and a 2x PNG preview."""
    svg_path = os.path.join(OUT, name + ".svg")
    fig.savefig(svg_path, format="svg", metadata={"Date": None, "Creator": None})
    fig.savefig(os.path.join(OUT, name + ".png"), format="png", dpi=192)
    with open(svg_path, encoding="utf-8") as fh:
        s = fh.read()
    i = s.index("<svg ")
    j = s.index(">", i) + 1
    head = s[i:j].replace("<svg ", '<svg role="img" aria-labelledby="t d" ', 1)
    s = s[:i] + head + f'\n <title id="t">{escape(title)}</title>\n <desc id="d">{escape(desc)}</desc>' + s[j:]
    with open(svg_path, "w", encoding="utf-8") as fh:
        fh.write(s)
    print("wrote", os.path.relpath(svg_path, ROOT), "+ .png")


def _caption(fig, lines, y0):
    for i, line in enumerate(lines):
        fig.text(0.5, y0 - i * 15 / (fig.get_figheight() * 96), line, ha="center", va="top", fontsize=11 * PX, color="#333333")


# ---------------------------------------------------------------- (e) pruning-point move cascade
def fig_pp_move_cascade():
    _require("findings/HTN-39.md", "+107.9 s", "+108.1 s", "4 s before t = 0", "243 s (A) and 207 s (B)")
    _require("findings/HTN-40.md", "| C (8 vCPU) | 2 min 5 s | 5 s | 1 min 57 s (94 %) | 1.6 s |",
             "| A (6 vCPU) | 4 min 3 s | 25 s | ~3 min 35 s (88 %)", "| B (6 vCPU) | 3 min 27 s | 45 s | 2 min 40 s (78 %)")
    _require("reports/memory-test.md", "| A, 7 GiB cap | 6 min 20 s | 1 min 55 s | 3 min 56 s | 26 s |",
             "| B, 7 GiB cap | 5 min 17 s | 1 min 23 s | 2 min 52 s | 60 s |")
    # seconds; deletion+commit None = not logged separately (folded into "other")
    upd = {  # node/case: (total, restore, scan, deletion+commit)
        "C, no cap": (125, 5, 117, 1.6),
        "A, no cap": (243, 25, 215, None),
        "A, 7 GiB cap": (380, 115, 236, 26),
        "B, no cap": (207, 45, 160, None),
        "B, 7 GiB cap": (317, 83, 172, 60),
    }
    arrival = {"C": 0.0, "A": 107.9, "B": 108.1}  # 5th move, relative to the start of C's update
    last_block = -4.0  # A and B processed their last block 4 s before t = 0
    for tot, r, s, d in upd.values():
        assert r + s + (d or 0) <= tot
    ends = {n: arrival[n] + upd[f"{n}, no cap"][0] for n in arrival}
    assert round(ends["A"]) == 351 and round(ends["B"]) == 315 and round(ends["C"]) == 125

    plt = _mpl()
    from matplotlib.patches import Patch
    fig = plt.figure(figsize=(700 / 96, 640 / 96))
    ax1 = fig.add_axes([0.12, 0.555, 0.84, 0.26])
    ax2 = fig.add_axes([0.12, 0.19, 0.84, 0.26])
    fig.text(0.5, 0.975, "Pruning-point move: stalls add up hop by hop (HTN-39, HTN-40)", ha="center", va="top",
             fontsize=16 * PX, fontweight="bold")
    phases = [("restore from acceptance data", ORANGE), ("commitment scan", BLUE), ("deletion + commit", GREEN),
              ("other / not logged separately", GREY_LIGHT)]

    def stacked(ax, y, x0, tot, r, s, d, h):
        widths = [r, s, d or 0, tot - r - s - (d or 0)]
        x = x0
        for w, (_, col) in zip(widths, phases):
            if w > 0:
                ax.barh(y, w, left=x, height=h, color=col, edgecolor="white", linewidth=0.5)
            x += w
        return x

    # panel a: timeline of the 5th move
    rows = ["C", "A", "B"]
    for i, n in enumerate(rows):
        y = len(rows) - 1 - i
        if arrival[n] > 0:
            ax1.barh(y, arrival[n] - last_block, left=last_block, height=0.5, color="white", edgecolor="#777777",
                     hatch="////", linewidth=0.6)
            ax1.text((last_block + arrival[n]) / 2, y, f"waiting until +{arrival[n]:.1f} s",
                     ha="center", va="center", fontsize=11 * PX, color=BLACK,
                     bbox=dict(boxstyle="square,pad=0.2", facecolor="white", edgecolor="none"))
        end = stacked(ax1, y, arrival[n], *upd[f"{n}, no cap"], h=0.5)
        ax1.text(end + 4, y, f"+{end:.0f} s", va="center", fontsize=12 * PX, fontweight="bold")
    ax1.axvline(0, color=VERMILION, linewidth=1, linestyle=(0, (4, 3)))
    ax1.text(2, 2.62, "t = 0: C starts its update", color=VERMILION, fontsize=11 * PX, va="bottom")
    ax1.set_yticks(range(len(rows)), [f"node {n}" for n in reversed(rows)])
    ax1.set_ylim(-0.5, 3.0)
    ax1.set_xlim(-20, 400)
    ax1.set_xlabel("time since C started its update (s)")
    ax1.set_title("a) 5th move: when each node updates; no blocks are processed in any bar", loc="left",
                  fontsize=12 * PX, fontweight="bold")
    ax1.grid(axis="y", visible=False)

    # panel b: phase durations without and with a 7 GiB memory cap
    cases = list(upd)
    for i, c in enumerate(cases):
        y = len(cases) - 1 - i
        end = stacked(ax2, y, 0, *upd[c], h=0.62)
        ax2.text(end + 4, y, f"{upd[c][0]} s", va="center", fontsize=12 * PX, fontweight="bold")
    ax2.set_yticks(range(len(cases)), list(reversed(cases)))
    ax2.set_xlim(0, 420)
    ax2.set_xlabel("duration of the pruning-point UTXO update (s)")
    ax2.set_title("b) update phases per node; the 7 GiB cap is a later move on the same nodes", loc="left",
                  fontsize=12 * PX, fontweight="bold")
    ax2.grid(axis="y", visible=False)

    handles = [Patch(facecolor="white", edgecolor="#777777", hatch="////", label="waiting, no blocks processed")]
    handles += [Patch(facecolor=col, label=lab) for lab, col in phases]
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.94), ncol=3, frameon=False,
               fontsize=11 * PX, handlelength=1.6, columnspacing=1.4)
    _caption(fig, ["A, B: 6 vCPU; C: 8 vCPU; HTND 2.18.1, same pruning point and blue score. A and B processed their last block",
                   "4 s before t = 0 and received the moving block from a peer that had finished its own update. Deletion + commit",
                   "was logged separately only for C and under the cap. Our node-log timings: findings/HTN-39.md, HTN-40.md, memory-test.md."],
             0.105)
    _save(fig, "pp-move-cascade",
          "Pruning-point move: per-node update timeline and phases",
          "Two panels. a) Fifth of five consecutive pruning-point moves, seconds relative to the start of node C's "
          "update. C updates from 0 to 125 s (restore 5 s, commitment scan 117 s, deletion and commit 1.6 s). Nodes A "
          "and B process no blocks from -4 s until the moving block arrives at +107.9 s and +108.1 s, then update for "
          "243 s and 207 s, ending at +351 s and +315 s. b) Update phases: C no cap 125 s; A no cap 243 s (restore 25, "
          "scan 215); A with a 7 GiB cap 380 s (restore 115, scan 236, deletion and commit 26); B no cap 207 s "
          "(restore 45, scan 160); B with the cap 317 s (restore 83, scan 172, deletion and commit 60).")
    plt.close(fig)


# ---------------------------------------------------------------- (f) bridge template cache before/after
def fig_gbt_cache():
    _require("findings/HTN-44.md", "46.7 % [44.8, 48.7] (1154/2469)", "8.5 % [7.3, 10.0] (144/1689)",
             "32.2 % (795/2469)", "0.18 % (3/1689)", "2.07 % [1.57, 2.71]", "0.95 % [0.58, 1.53]",
             "8.05 %", "6.78 %", "+0.15 pp, 95 % CI [−0.61, +0.91]")
    counts = {  # metric: (before k, n), (after k, n)
        "missed": ((1154, 2469), (144, 1689)),
        "missed50": ((795, 2469), (3, 1689)),
        "own_red": ((51, 2469), (16, 1689)),
        "oth_red": ((11591, 143955), (6750, 99513)),
    }
    ci = {m: [_wilson(*kn) for kn in v] for m, v in counts.items()}
    # the Wilson intervals must reproduce the published rounding
    assert [round(100 * x, 1) for x in ci["missed"][0]] == [46.7, 44.8, 48.7]
    assert [round(100 * x, 1) for x in ci["missed"][1]] == [8.5, 7.3, 10.0]
    assert [round(100 * x, 2) for x in ci["own_red"][0]] == [2.07, 1.57, 2.71]
    assert [round(100 * x, 2) for x in ci["own_red"][1]] == [0.95, 0.58, 1.53]
    assert [round(100 * ci["oth_red"][i][0], 2) for i in (0, 1)] == [8.05, 6.78]

    plt = _mpl()
    from matplotlib.patches import Patch
    fig = plt.figure(figsize=(700 / 96, 440 / 96))
    ax1 = fig.add_axes([0.09, 0.27, 0.39, 0.53])
    ax2 = fig.add_axes([0.59, 0.27, 0.39, 0.53])
    fig.text(0.5, 0.97, "Bridge template cache: before and after the fix (HTN-44)", ha="center", va="top",
             fontsize=16 * PX, fontweight="bold")
    colours = (ORANGE, BLUE)

    def panel(ax, metrics, labels, ymax, fmt):
        w = 0.36
        for j, m in enumerate(metrics):
            for k in (0, 1):
                p, lo, hi = ci[m][k]
                x = j + (k - 0.5) * (w + 0.04)
                ax.bar(x, 100 * p, width=w, color=colours[k])
                ax.errorbar(x, 100 * p, yerr=[[100 * (p - lo)], [100 * (hi - p)]], color=BLACK, capsize=3,
                            linewidth=0.8)
                ax.text(x, 100 * hi + ymax * 0.02, fmt(100 * p), ha="center", va="bottom", fontsize=11 * PX,
                        fontweight="bold")
        ax.set_xticks(range(len(metrics)), labels)
        ax.set_ylim(0, ymax)
        ax.grid(axis="x", visible=False)

    panel(ax1, ["missed", "missed50"], ["known tip missing\n(any age)", "known tip missing,\n≥ 50 ms old"], 60,
          lambda v: f"{v:.2f} %" if v < 1 else f"{v:.1f} %")
    ax1.set_ylabel("share of own blocks (%)")
    ax1.set_title("a) stale templates: significant drop", loc="left", fontsize=12 * PX, fontweight="bold")
    panel(ax2, ["own_red", "oth_red"], ["own miner", "all other miners\n(control)"], 10, lambda v: f"{v:.2f} %")
    ax2.set_ylabel("red share of blocks (%)")
    ax2.set_title("b) red share: not significant", loc="left", fontsize=12 * PX, fontweight="bold")
    ax2.text(0.25, 0.80, "pre-registered DiD\n+0.15 pp, 95 % CI\n[−0.61, +0.91]:\nnot significant",
             transform=ax2.transAxes, ha="center", va="top", fontsize=11 * PX, color=VERMILION)
    fig.legend(handles=[Patch(facecolor=ORANGE, label="before (~9 h)"), Patch(facecolor=BLUE, label="after (~6 h)")],
               loc="upper center", bbox_to_anchor=(0.5, 0.905), ncol=2, frameon=False, fontsize=12 * PX)
    _caption(fig, ["One solo miner behind the fixed bridge; 15 min after each pruning-point move excluded. Error bars: Wilson 95 %",
                   "intervals. Exploratory, not pre-registered: relative-risk ratio 0.54 [0.31, 0.95]. Sources: findings/HTN-44.md,",
                   "reports/red-blocks.md."], 0.13)
    _save(fig, "gbt-cache-before-after",
          "Bridge template cache before and after the fix",
          "Two panels with Wilson 95 % intervals. a) Own blocks missing a tip the node already knew: before 46.7 % "
          "(1154/2469), after 8.5 % (144/1689); with the tip at least 50 ms old: before 32.2 %, after 0.18 %. b) Red "
          "share: own miner before 2.07 %, after 0.95 %; all other miners before 8.05 %, after 6.78 %. Pre-registered "
          "difference-in-differences +0.15 pp, 95 % CI -0.61 to +0.91: not significant.")
    plt.close(fig)


if __name__ == "__main__":
    fig_red_blocks()
    fig_pow_fma()
    fig_memory_budget()
    fig_parent_count()
    try:
        import matplotlib  # noqa: F401
    except ImportError:
        print("matplotlib not installed: skipped pp-move-cascade and gbt-cache-before-after")
    else:
        fig_pp_move_cascade()
        fig_gbt_cache()
