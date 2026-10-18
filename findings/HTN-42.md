# HTN-42 — Install script and sample systemd unit are stored with CRLF line endings; the script does not parse

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Low | tooling | Reproduced | none | PR | Draft — not yet submitted | TBD |

## Summary

`start-htnd.sh` (455 lines, all ending in CRLF) and `deploy/htnd.service` (71 CRLF lines) are committed with Windows
line endings. Bash reads the carriage return as part of each line, and `bash -n start-htnd.sh` stops with a syntax
error at line 26 (`need_cmd() {`). The script's own header documents running it directly and piping it from GitHub to
bash; both depend on it parsing.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `start-htnd.sh`, `deploy/htnd.service`
- `.gitattributes` normalises only `*.go`
- The line endings arrived with the 2.18.0 import commit `3952a6ca4`; the script parsed before it. Same state in
  v2.18.0, v2.18.1 head `fcef4aede` and master `c097146c6`.

## Impact

New operators who follow the documented one-line install get a syntax error instead of a node. The effect of CRLF on
systemd parsing of the sample unit was not tested.

## Evidence

```
git show a56566e86:start-htnd.sh | bash -n
bash: line 26: syntax error near unexpected token `{'
git show a56566e86:start-htnd.sh | tr -d '\r' | bash -n   # parses
git show 3952a6ca4^:start-htnd.sh | bash -n                # parses
```

## Recommendation

Convert both files to LF and add `*.sh text eol=lf` and `*.service text eol=lf` to `.gitattributes`, so that a future
import cannot reintroduce CRLF. No content change. Optionally a CI step that runs `bash -n` on shell scripts (fits
HTN-19).

## Verification

**Completed:** reproduced at `a56566e86`, `fcef4aede`, `v2.18.0` and `c097146c6`; LF conversion parses.

**Required before submission:** run the converted script end to end on a clean Linux VM (download path and prompts);
`systemd-analyze verify` on the converted unit.

## Chain impact

None (install tooling).

## Related items

[HTN-35](HTN-35.md), [HTN-19](HTN-19.md)

## Upstream

TBD — PR/issue link to be filled in once submitted.

