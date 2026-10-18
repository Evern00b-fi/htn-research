# HTN-25 — PoW build tags leave linux/arm64 without cgo uncovered

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Low | tooling | Reproduced | none | PR | Draft — not yet submitted | TBD |

## Summary

`pow.go` is tagged `!linux || !arm64` and `pow_aarch64_linux.go` is `linux && arm64 && cgo`; linux/arm64 with
`CGO_ENABLED=0` has no PoW implementation. `go-muhash` also requires cgo, so a cgo-free linux/arm64 build still fails
for a separate reason.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `domain/consensus/utils/pow/pow.go` (build tag), `pow_aarch64_linux.go`

## Impact

Cross-compilation for linux/arm64 without cgo fails in the PoW package with a confusing `undefined` error rather than
a clear "unsupported" message. Operators who want a static binary for ARM single-board computers hit this first. The
masking by `go-muhash` means that fixing the tag alone does not yet make the build succeed, which is why this is a
small, separate PR rather than part of HTN-01.

## Evidence

`GOOS=linux GOARCH=arm64 CGO_ENABLED=0 go build .` fails with `undefined: pow.BlockLevel`.

## Recommendation

Change the first tag to `!(linux && arm64 && cgo)` so the Go implementation is selected whenever the C path is not.
The MuHash cgo dependency is a separate issue. After HTN-01 lands, maintainers may also want to consider whether the
prebuilt C library (two binary blobs without source in the repository) is still needed, since the Go path would then
agree with it; that decision belongs with HTN-16.

## Verification

**Completed:** `CGO_ENABLED=0` cross-compile fails as described.

**Required before submission:** the PoW package builds under `CGO_ENABLED=0` for linux/arm64 after the change.

## Chain impact

None (build).

## Related items

[HTN-16](HTN-16.md)

## Upstream

TBD — PR/issue link to be filled in once submitted.

