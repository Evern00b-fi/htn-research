# HTN-31 — Bridge: block counters record every accepted pool share as a found block

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Low | tooling | Reproduced | none | PR | Draft — not yet submitted | TBD |

## Summary

Commit `9574695` moved block accounting from the successful-submission path into the accepted-share tail, so one
ordinary pool share produces worker, overall and Prometheus block counts of 1 instead of 0. The hash/nonce label is
also computed from a clone whose nonce is never set.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `htn-stratum-bridge/src/htnstratum/share_handler.go:434-436, 454-459` @3b2cf8c

## Impact

Wrong block statistics and labels in pool mode: worker and overall block counters, the Prometheus block metric and
the "block found" log line fire on every accepted share. Validation, replies and submission are unaffected, so this is
accounting only, but pool operators cannot tell real blocks from shares in their dashboards.

## Evidence

Test: a pool share yields 1 block (expected 0); a submission with nonce 1 is recorded as nonce 0 with a different hash.

## Recommendation

Move both block counters and `RecordBlockFound` into `submit`, after `SubmitBlock` returns nil, using the nonce-set
block. Validation, replies, removal and callbacks unchanged.

## Verification

**Completed:** pool-share and nonce-label regression tests fail on main and pass after the fix.

**Required before submission:** the tests included in the PR; duplicate, invalid-PoW and RPC-error cases still count zero blocks.

## Chain impact

None (pool software).

## Related items

[HTN-20](HTN-20.md), [HTN-32](HTN-32.md)

## Upstream

TBD — PR/issue link to be filled in once submitted.

