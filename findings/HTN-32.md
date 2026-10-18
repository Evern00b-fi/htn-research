# HTN-32 — Bridge: shared tip blue score is read and written without synchronisation

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Low | tooling | Reproduced | none | PR | Draft — not yet submitted | TBD |

## Summary

`tipBlueScore` in the share handler is read by every client handler's stale check and written whenever a newer
submission arrives, with no synchronisation; `-race` reports a read/write race between handlers.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `htn-stratum-bridge/src/htnstratum/share_handler.go:286-288` @3b2cf8c

## Impact

Data race on a value that every share check reads: a delayed writer could lower the recorded tip and turn a fresh
share into a "stale" rejection (the eight-score rule), or a stale share into an accepted one. The value is defined
historically as the highest observed submission score, not a freshly queried node tip; the fix preserves that meaning.

## Evidence

`TestAuditB5ConcurrentCheckStales` (`go test -race ./src/htnstratum/ -run TestAuditB5`) reports the read/write race on
main and passes after the fix, including the eight-score acceptance and nine-score rejection cases. Plain atomic
load/store would not be enough: a delayed writer could still lower the tip, hence the compare-and-swap maximum.

## Recommendation

Use the already-imported `go.uber.org/atomic.Uint64` with a compare-and-swap maximum (advance-only).

## Verification

**Completed:** the race test reports the race on main and passes after the fix.

**Required before submission:** the test included in the PR.

## Chain impact

None (pool software).

## Related items

[HTN-20](HTN-20.md), [HTN-31](HTN-31.md)

## Upstream

TBD — PR/issue link to be filled in once submitted.

