# HTN-34 — CI toolchain pin disagrees with `go.mod`

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Informational | tooling | Code-confirmed | none | PR | Draft — not yet submitted | TBD |

## Summary

`tests.yaml` and `deploy.yaml` pin `go-version: 1.26`, while `go.mod` requires Go 1.27. The workflows therefore rely on
the toolchain directive to fetch a newer Go at run time rather than building with the version they declare, and the
release binaries are not built with a pinned, reviewed toolchain.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `.github/workflows/tests.yaml`, `.github/workflows/deploy.yaml`, `go.mod`

## Impact

Builds depend on toolchain auto-download behaviour rather than the declared version; a future `go.mod` bump could
silently change the compiler used for releases. Split from the architecture-coverage change (HTN-24) so each is one decision.

## Evidence

Files read at a56566e86: `go-version: 1.26` in both workflows; `go 1.27` in `go.mod`. The offline test environment
used for this review had to run Go 1.27.2 for the module to build at all.

## Recommendation

Set `go-version` to the `go.mod` version (or use `go-version-file: go.mod`) in both workflows. One-line change per file; rollback is a revert.

## Verification

**Completed:** files read.

**Required before submission:** CI builds with the declared toolchain and the workflow logs show the expected Go version.

## Chain impact

None.

## Related items

[HTN-19](HTN-19.md)

## Upstream

TBD — PR/issue link to be filled in once submitted.

