# HTN-43 — A damaged record in an older WAL forces a full resync; a point-in-time WAL cut could avoid it (research)

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Low | storage | Reproduced | none | PR | Prototype — not ready (review: transient read errors cause extra loss 364→243 keys; missing durability barrier; depends on the pruning-flag fix) | TBD |

## Summary

Pebble replays every live WAL in order. Newest-WAL damage is truncated silently (HTND writes NoSync); a damaged
record in an older WAL fails the open with `ErrCorruption`, and HTND deletes the datadir and resyncs (HTN-03), although
the data before the damaged record is intact. RocksDB handles this by default (point-in-time recovery, inherited by
rusty-kaspa); pebble has no such option. **The idea and the Kaspa comparison are research; the prototype is not a
ready fix.**

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `infrastructure/db/database/pebble/pebble.go` (`NewPebbleDB` corruption path)
- pebble v2.1.6 `open.go` (WAL replay and its strict-tail rule for older WALs)

## Impact

A full IBD where a cut plus a re-download of the dropped tail could suffice. The dropped amount is not a fixed bound
(configurable memtables, large batches; a node offline for long may restart behind its peers' pruning point). It
needs damage to an already-synced older WAL, so it is rare.

## Evidence

`TestNewPebbleDBRepairsADamagedOlderWAL`: 487 commits over three unflushed WALs, four bytes inverted in the second.
The HTN-03 branch alone keeps 0 keys; the prototype keeps the 364-key prefix (243 from the first WAL plus 121 from the
damaged one), as the review reproduced. A consensus-level test on both nets restarts on a strict block prefix and
accepts the lost blocks again.

## Recommendation

Prototype on top of HTN-03 (+912/−34 lines in 7 files, 676 of them tests; core about 195 lines): on `ErrCorruption`,
under the lifecycle lock, read the damaged WAL number from pebble's error, recompute the cut with pebble's reader, write
diagnostics and a synced prefix copy, move later WALs aside and rename the copy over the damaged WAL. Review blockers:
a transient read error counts as corruption (one failed `Open` keeps 243 instead of 364 keys); later-WAL removals are
not synced before the replacement; without the pruning-flag fix (HTN-02) a cut after the deletion commit leaves a
node that cannot start. See [reports/db-recovery.md](../reports/db-recovery.md).

## Verification

**Completed:** the tests above, injected I/O failures at five steps, a test pinning pebble's error text, leftover and
disk-statistics tests; all pass with `-race`. Not covered: transient reads, short copies, power-loss ordering.

**Required before submission:** separate I/O errors from corruption and require an exact-length prefix copy; sync the
removals before the replacement; HTN-02 as an explicit dependency, with WAL cuts tested through its transition; HTN-03
reworked first; several populated later WALs; relay/IBD catch-up observed end to end.

## Chain impact

None (node-local). A repaired datadir is an ordinary pebble datadir.

## Related items

[HTN-03](HTN-03.md), [HTN-27](HTN-27.md), [HTN-02](HTN-02.md)

## Upstream

TBD — PR/issue link to be filled in once submitted.

