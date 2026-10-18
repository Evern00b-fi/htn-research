# HTN-27 — Durability: no bounded sync point for acknowledged writes

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Low | storage | Reproduced | none | Issue | Draft — not yet submitted | TBD |

## Summary

All writes are `NoSync`. A process crash can lose buffered NoSync writes; power loss can additionally lose
unsynced OS-cached data. No upper bound on the loss is established (an earlier "<= 32 KiB" claim was refuted: a
targeted test queued more than 256 KiB). State stays prefix-consistent. Synced commits were tried in `2117e1e10` and
reverted the same day (IBD too slow). kaspad and rusty-kaspa also write without sync.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `infrastructure/db/database/pebble/transactions.go:70`, `pebble.go:105-154`, `options.go:123`

## Impact

Recent acknowledged blocks are re-fetched after a crash; combined with HTN-02 the lost write can be the one
that matters.

## Evidence

- `TestS1AcknowledgedCommitSurvivesPowerLoss` fails (acceptance test for a future sync point).
- 200 simulated power-loss images (40 transactions each): 0 open errors, every transaction all-or-nothing, survivors
  always a prefix; 1760 of 8000 acknowledged transactions lost.
- Second reviewer's `wal_bound_test.go`: `WriteRecord` returned with > 256 KiB queued while the underlying write could not complete.

## Recommendation

Options: (a) do nothing; (b) one `LogData(nil, Sync)` per second after an IBD benchmark; depends on HTN-03 and
HTN-07 (once commits sync, damage before a synced offset is reported as corruption). Recommendation: benchmark first.
Decision requested: is bounded loss acceptable, or is (b) wanted?

## Verification

**Completed:** durability tests; 200 simulated power-loss images; the second reviewer's > 256 KiB queue test.

**Required before submission:** the acceptance test with a ticker hook; an IBD benchmark on reference hardware.

## Chain impact

None (node-local).

## Related items

[HTN-03](HTN-03.md), [HTN-07](HTN-07.md), [HTN-05](HTN-05.md)

## Upstream

TBD — PR/issue link to be filled in once submitted.

