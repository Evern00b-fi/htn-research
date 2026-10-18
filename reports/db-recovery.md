# Database recovery: fault model, a candidate light repair (research), and Kaspa

Related findings: [HTN-02](../findings/HTN-02.md), [HTN-03](../findings/HTN-03.md), [HTN-43](../findings/HTN-43.md),
[HTN-17](../findings/HTN-17.md), [HTN-27](../findings/HTN-27.md). Code: HTND v2.18.1 head `fcef4aede`, pebble v2.1.6.
This page explains why the recovery proposals are ordered as they are. It is reasoning from code plus tests. **The
cause of the corruption our own nodes hit in the past is unknown**, because no pebble error line from those incidents
was kept.

## What can damage a NoSync pebble database

HTND writes with `NoSync`. A WAL record is written into the writer's 32 KiB block; full blocks are queued in user space
and flushed asynchronously (`record/log_writer.go:827-845`), so at any moment the process can hold the block being
filled plus several queued full blocks. A rotation syncs the previous WAL before the next one exists; MANIFEST edits are
synced before they are applied; flushed sstables are synced before the edit that adds them.

| Fault | What is lost or damaged | What fixes or prevents it |
|---|---|---|
| OOM kill of the node process (SIGKILL; the page cache survives) | Unflushed WAL data queued in user space: the current block and possibly further queued full blocks. No upper bound is established (HTN-27). Pebble treats the loss as a truncated tail of the newest WAL and opens without `ErrCorruption`. | Nothing to repair in pebble. If the lost data includes the commit that clears the pruning flag, the node cannot start: **HTN-02**. A memory budget from host RAM (HTN-17) reduces the trigger. |
| VM kill or power loss on honest storage | The unsynced tail of the newest WAL, possibly with holes; pebble truncates at the first hole. Crash-image tests (200 images) always gave a commit prefix. | As above, with a larger lost tail. |
| Storage that loses synced writes (e.g. a write-back cache without power-loss protection) | Any file. | v2.18.1 already deletes the datadir and syncs fresh. **HTN-03** (draft, rework required) adds best-effort diagnostics before that. Damage in an older WAL: **HTN-43** (research prototype, not ready). |
| Crash at the pruning move's memory peak, flag set | Nothing is corrupted; the state is a prefix HTND cannot resume because the blocks the resumption needs were already deleted. | **HTN-02**. Not a pebble corruption, so the corruption path of HTN-03 and HTN-43 is not reached. |

**Conclusion.** By this reading of pebble and our crash-image tests, an OOM kill on honest storage does not produce
pebble `ErrCorruption`; it loses a tail of the newest WAL. The cause of our past incidents is still unknown. The
pruning-flag case (HTN-02) is one plausible candidate for a node that will not start after an OOM kill; it is not
established as the cause. Order that follows: HTN-02 first (a reproduced defect, whatever the incidents' cause), HTN-17
(reduces OOM kills), HTN-03 (v2.18.1 already deletes on corruption; the draft adds diagnostics before the fresh sync and
needs rework), HTN-43 (research; not a ready fix).

## Corruption classes and the lightest correct repair

| Class | Detected | Pebble today | Lightest correct repair | Re-downloaded |
|---|---|---|---|---|
| Newest WAL: bad record or unclean tail | at open | truncated silently, opens | none needed (this is point-in-time recovery) | commits after the cut |
| Older WAL: bad record | at open | `ErrCorruption`, open fails | candidate: **cut that WAL at the first unreadable record, set later WALs aside, open** (HTN-43 prototype, not ready) | the dropped tail: unflushed memtables and later WALs. Not a fixed bound: memtable options are configurable and large batches exist; a node offline for long may restart behind its peers' pruning point and need a headers-proof IBD anyway |
| MANIFEST: invalid record | at open | truncated without an error (`version_set.go:246-260`); tables of lost edits deleted as obsolete | none that is light; can leave a non-prefix that nothing reports | full IBD |
| MANIFEST: malformed marker name | at open | reported as corruption | none that is light | full IBD |
| sstable block or footer | at read time, after a successful open | read fails; the node's flow panics and it crash-loops | none that is light: dropping a table un-shadows older values, and stored objects cannot be re-fetched piecemeal | full IBD |

Why a WAL cut can be correct (the premise, not a proof of the prototype): replay and flush follow WAL order, so durable
state is "all batches of older WALs plus a prefix of the next". This holds only when the MANIFEST and sstables are sound
and the later WALs are durably excluded. Every block insertion is one batch; HTND's multi-commit operations must also
resume from the resulting prefix. The pruning-point UTXO update does not yet do so after its deletion commit (HTN-02),
so the WAL cut depends on that fix. A consensus-level test restarts a real node on a strict block prefix after the
repair and accepts the lost blocks again.

Some MANIFEST damage (an invalid record) is truncated without an error today; other damage, such as a malformed marker
name, is reported as corruption. Detecting the silent case would need a cheap consensus-level startup check or a
validated checkpoint; both are listed as follow-ups, not proposed yet.

## Kaspa comparison (research)

| | On corruption at open | WAL recovery | Deletes the database |
|---|---|---|---|
| kaspad (goleveldb, NoSync) | `leveldb.RecoverFile`: ignores the MANIFEST, rescans tables, rebuilds or drops corrupt ones, rewrites the MANIFEST in place | non-strict replay skips a corrupt batch and continues, so a non-prefix state is possible | never |
| rusty-kaspa (RocksDB) | no recovery code; RocksDB defaults | RocksDB's default point-in-time recovery: the same idea as the HTN-43 prototype, built in | only on `--reset-db`, a database-version change, or a missing genesis on non-mainnet, after confirmation |
| HTND 2.18.1 | deletes the datadir and starts empty, with a Warn log (HTN-03) | newest WAL truncated by pebble; older WAL fails the open | automatically, without evidence |
| HTND with the HTN-03 and HTN-43 drafts (not ready; for comparison only) | best-effort diagnostics bundle; older-WAL damage cut in place; anything else fresh | the same idea as rusty-kaspa | automatically, never on a disk measurement |

rusty-kaspa has point-in-time WAL behaviour by inheritance from RocksDB and nothing for sstables; kaspad's in-place
rebuild rewrites the only copy and accepts a non-prefix.

## Limits

- Network catch-up after a repair was fed by the test, not observed through the relay and IBD flows.
- The repair reads the damaged WAL number from pebble's error text; a test pins it, so a pebble upgrade that changes
  the text makes the repair decline rather than misfire.
- No real power-loss test; pebble's crashable in-memory file system was used.
- An adversarial review of the HTN-03 and HTN-43 drafts found blockers (listed in those findings). Neither draft is
  ready to submit.
