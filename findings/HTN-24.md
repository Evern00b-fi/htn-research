# HTN-24 — CI does not run the PoW package on every release architecture

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Low | tooling | Code-confirmed | none | PR | Draft — not yet submitted | TBD |

## Summary

The `pow` package has no Hoohash test vectors (its only test is `xoshiro_test.go`), CI runs amd64 only (ubuntu and
windows runners) and does not pin `GOAMD64`, so HTN-01 could not have been caught by any automated check. The release
workflow builds the macOS asset on an arm64 runner, i.e. the one architecture whose output the tests never see.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `.github/workflows/tests.yaml`, `domain/consensus/utils/pow/`

## Impact

Platform-dependent PoW regressions reach releases unexecuted; after HTN-01 is merged, nothing would prevent a later
change from re-introducing fusion or a libm-dependent path (HTN-16).

## Evidence

Workflow and package read at a56566e86.

## Recommendation

Add `macos-latest` and `ubuntu-24.04-arm` runners for the `pow` package only (the full suite is slow; the PoW package
is fast), with the C library on and off on linux/arm64, and pin `GOAMD64` explicitly in the amd64 jobs. Depends on
HTN-01's vector test. Rollback: remove the matrix entries. Kept separate from HTN-34 so each is one decision.

## Verification

**Completed:** workflow read.

**Required before submission:** the vector test runs and passes on every matrix entry.

## Chain impact

None (CI).

## Related items

[HTN-01](HTN-01.md), [HTN-16](HTN-16.md)

## Upstream

TBD — PR/issue link to be filled in once submitted.

