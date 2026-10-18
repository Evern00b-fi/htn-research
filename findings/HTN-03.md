# HTN-03 — Datadir is deleted on Pebble corruption at open; no evidence is kept

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| High | storage | Reproduced | none | PR | Draft — rework required (review found blockers: lock failure must fail closed, missing-parent regression, no deletion-in-place fallback, bundle is best-effort diagnostics, not a protected copy) | TBD |

## Summary

`NewPebbleDB` runs `os.RemoveAll(datadir)` when `pebble.Open` reports `ErrCorruption`, logs at Warn and starts
empty with a full IBD. The path was dead code until commit `882fe4914` (first tagged in v2.17.3) made the error match.
kaspad repairs in place; rusty-kaspa asks before deleting.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `infrastructure/db/database/pebble/pebble.go:46-56`
- Commits `0ba4f5b39` (introduced, inert), `882fe4914` (made live)

## Impact

A corrupted node automatically resets itself after warning logs, destroys the evidence needed to diagnose the
corruption and spends hours re-syncing. Before v2.17.3 the node refused to start instead. On a failing parent
directory `RemoveAll` unlinks the WAL and sstables before it returns an error (reproduced on a read-only parent), and
nothing stops a second opener from acting on the directory during the replacement.

## Evidence

- `TestS1OpenPreservesEvidence/wal-corruption`: the evidence file is gone and `err == nil`.
- Transient conditions did **not** trigger the wipe in the tested set: lock held by another process, stale `LOCK`
  file, EACCES on MANIFEST, injected EMFILE / EIO / ENOSPC, missing or truncated `.sst`. This is not a proof
  that no other condition does.
- Fault model ([reports/db-recovery.md](../reports/db-recovery.md)): by our reading, an OOM kill or a crash on honest
  storage loses a newest-WAL tail without `ErrCorruption`; this path is expected on media damage. The cause of our own
  past incidents is unknown.

## Recommendation

The earlier quarantine proposal was superseded (unbounded disk use, no lock against a second opener). The draft PR
keeps v2.18.1's fresh sync and adds a lifecycle lock for cooperating openers (pebble's file lock, an fcntl record lock
on Unix) and a size-bounded diagnostics bundle (pebble error, file listing, MANIFEST/OPTIONS, named damaged files)
before the old datadir is deleted. The bundle is best-effort diagnostics (not fsynced), not a protected copy. Review
blockers: a failed lock must fail closed; the parent must be created before locking (fresh nested paths regress); a
failed rename must return its error instead of deleting in place; non-ENOENT `Lstat` errors must be returned instead
of looping.

## Verification

**Completed:** seven tests (bundle, read-only parent, second opener refused, leftovers, rotation, size bound,
disk statistics) pass on the branch, also with `-race`; the review reproduced the base failures and found the
lock-bypass and missing-parent regressions.

**Required before submission:** the four corrections above with regression tests; failure tests for bundle rotation
and cleanup; wording limited to what is tested (cooperating openers only, best-effort diagnostics).

## Chain impact

None (node-local).

## Related items

[HTN-43](HTN-43.md), [HTN-02](HTN-02.md), [HTN-27](HTN-27.md), [HTN-07](HTN-07.md)

## Upstream

TBD — PR/issue link to be filled in once submitted.

