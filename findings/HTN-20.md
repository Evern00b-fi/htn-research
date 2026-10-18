# HTN-20 — Bridge: job slots are overwritten without an ownership check

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Medium | tooling | Reproduced | none | PR | Merged 2026-10-17 into 1.8.2 (2f5f25cc3) | PR [bridge#12](https://github.com/HoosatNetwork/htn-stratum-bridge/pull/12) |

## Summary

In `htn-stratum-bridge` v1.8.0 the mining state confuses slot identity with job identity: a job's ring slot is
overwritten without checking the owner, `RemoveJob` can delete a newer job that reused the slot, and the job number is
taken outside the lock.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `htn-stratum-bridge/src/htnstratum/mining_state.go:37-61` @3b2cf8c
- Commits `572c711` (increasing IDs over modulo slots), `dde3e50` (unconditional slot deletion), `73466bb` (missing job = stale)

## Impact

Valid shares can be judged stale or attributed to the wrong job; a race is reported under `-race`.

## Evidence

Two tests fail on main ("job 1 resolved ... reused by job 33", plus races at `mining_state.go:38-39`); the
patched version passes 20 race-enabled runs. An additional test confirms that removing an old ID deletes the newer job
before the fix and preserves it after.

## Recommendation

Ownership-tagged slots and locked allocation. Risk: low; capacity and submission policy unchanged. The exported
`Jobs` element type changes (no other in-repository users).

## Verification

**Completed:** two tests fail on main; the patched version passes 20 race-enabled runs.

**Required before submission:** the tests included in the PR.

## Chain impact

None (pool software).

## Related items

[HTN-31](HTN-31.md), [HTN-32](HTN-32.md)

## Upstream

PR [bridge#12](https://github.com/HoosatNetwork/htn-stratum-bridge/pull/12) — in review.

