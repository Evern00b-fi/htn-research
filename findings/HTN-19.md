# HTN-19 — Per-push CI runs almost no unit tests

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Medium | process | Code-confirmed | none | PR | Draft — not yet submitted | TBD |

## Summary

`build_and_test.sh` has `go test` commented out and the stability script exits 0. CI is not test-free:
`tests.yaml` runs 4 named tests plus `-race` on `rpcclient`, and `race.yaml` runs `go test -race ./...` nightly
(its workflow results were not inspected by this review). Per-push coverage is near zero. In a 39-package subset at a56566e86 at least 11 tests fail,
including five pruning-import / headers-proof tests whose cause (fixture or defect) is not yet classified.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `build_and_test.sh:56-62`, `stability-tests/install_and_test.sh:21`
- `.github/workflows/tests.yaml`, `.github/workflows/race.yaml`

## Impact

Regressions on consensus paths can reach a release unexecuted.

## Evidence

Scripts and workflows read at a56566e86; test subset run offline (`go test -tags=ci ...` on 39 packages):
11 failures in 7 packages; `-race` on `./app/protocol/...` found no data race.

## Recommendation

Re-enable `go test -tags=ci ./...` with `-skip` for known failures, each commented with an issue link. No green CI is
promised: a full-suite baseline run on the CI runners must come first and may extend the list.

## Verification

**Completed:** 39-package offline run (11 failures); `-race` run on `./app/protocol/...` (no race).

**Required before submission:** a full-suite baseline on the CI runners; the skip list, which must shrink over time.

## Chain impact

None (node-local).

## Related items

[HTN-21](HTN-21.md), [HTN-24](HTN-24.md), [HTN-34](HTN-34.md)

## Upstream

TBD — PR/issue link to be filled in once submitted.

