# Changes by area

Every change we have sent to the Hoosat developers. Status checked against GitHub on 18 October 2026.

| Mark | Meaning |
|---|---|
| ✅ Released | In a public Hoosat release; you get it by updating |
| 🔀 Merged | Accepted by the Hoosat developers; ships in the next release |
| 🔄 In review | Sent to the Hoosat developers; waiting for their decision |
| 🧪 Being tested | Fix written; being measured before it is sent |
| 📝 Proposed | Written up here; not yet sent |

Totals on 18 October 2026: HTND pull requests 8 released, 18 merged, 8 in review; HTND issues 7 in review; bridge pull requests 4 merged, 1 in review. Nothing has been closed or rejected.

## By release

- **HTND v2.18.2**, 16 October 2026: 8 changes — [HTND#36](https://github.com/HoosatNetwork/HTND/pull/36), [HTND#37](https://github.com/HoosatNetwork/HTND/pull/37), [HTND#38](https://github.com/HoosatNetwork/HTND/pull/38), [HTND#39](https://github.com/HoosatNetwork/HTND/pull/39), [HTND#40](https://github.com/HoosatNetwork/HTND/pull/40), [HTND#44](https://github.com/HoosatNetwork/HTND/pull/44), [HTND#46](https://github.com/HoosatNetwork/HTND/pull/46), [HTND#47](https://github.com/HoosatNetwork/HTND/pull/47)

## 1. Stopping and restarting a node

| What changed | Status | Version | Link |
|---|---|---|---|
| A node that is stopped while busy no longer crashes with "database closed": if a safe stop does not finish in time, it exits without closing the database and recovers from its write-ahead log at the next start | ✅ Released | v2.18.2 | [HTND#37](https://github.com/HoosatNetwork/HTND/pull/37) |
| The node waits for running RPC requests before closing the database | ✅ Released | v2.18.2 | [HTND#46](https://github.com/HoosatNetwork/HTND/pull/46) |
| Stopping no longer hangs when a new peer connects while the node is shutting down | ✅ Released | v2.18.2 | [HTND#40](https://github.com/HoosatNetwork/HTND/pull/40) |
| Stopping no longer hangs on waking a connection loop that has already ended | ✅ Released | v2.18.2 | [HTND#36](https://github.com/HoosatNetwork/HTND/pull/36) |
| A connection's message router is counted before its worker starts, so shutdown waits for it | 🔀 Merged | 2.18.3 | [HTND#48](https://github.com/HoosatNetwork/HTND/pull/48) |
| The peer handshake waits for both of its workers before returning | 🔀 Merged | 2.18.3 | [HTND#49](https://github.com/HoosatNetwork/HTND/pull/49) |
| The address manager stops writing to the database once the node has stopped | 🔀 Merged | 2.18.3 | [HTND#50](https://github.com/HoosatNetwork/HTND/pull/50) |
| In-memory tables are written out at close when the write-ahead log is disabled | 🔀 Merged | 2.18.3 | [HTND#51](https://github.com/HoosatNetwork/HTND/pull/51) |
| The node guide's systemd unit gets a stop timeout longer than the node's own, so systemd does not kill a node mid-shutdown | 🔀 Merged | 2.18.3 | [HTND#52](https://github.com/HoosatNetwork/HTND/pull/52) |
| Log lines written after the logger is closed go to stderr instead of crashing the process | 🔀 Merged | 2.18.3 | [HTND#53](https://github.com/HoosatNetwork/HTND/pull/53) |
| A stop request ends the wait before an automatic update install | 🔄 In review | — | [HTND#54](https://github.com/HoosatNetwork/HTND/pull/54) |
| An opt-in stress test that starts and stops the node many times to catch shutdown bugs (test only) | 🔄 In review | — | [HTND#55](https://github.com/HoosatNetwork/HTND/pull/55) |

<details>
<summary>Technical details: shutdown</summary>

- Findings: [HTN-05](findings/HTN-05.md) (database closed under active users when the graceful shutdown times out;
  observed on our node as `pebble: closed`, exit 1), [HTN-06](findings/HTN-06.md) (NetAdapter accepted P2P connections
  while stopping), [HTN-41](findings/HTN-41.md) (`ConnectionManager.Stop` blocked forever on a returned loop),
  [HTN-35](findings/HTN-35.md) (guide's unit lacks `TimeoutStopSec`; the node's outer timeout is 120 s and includes the
  90 s event drain).
- The eight open pull requests #48–#55 were prepared with the help of a shutdown stress harness (#55) on the 2.18.2
  branch after the first four fixes were merged; each carries its own regression test. #48 and #50 link to the harness.
- Merge commits on the 2.18.2 branch: #36 `5b1c9e3b6`, #37 `c36ba8c3d`, #40 `717a3366c`, #46 `e6eb0bb82`.
- A refuted claim worth knowing: the internal shutdown budget is not "about 210 s"; see
  [METHODOLOGY.md](METHODOLOGY.md#4-what-was-refuted-or-corrected).

</details>

## 2. Keeping your node's data safe

| What changed | Status | Version | Link |
|---|---|---|---|
| A crash during the pruning clean-up no longer leaves the node unable to start (it used to fail with `blockHash is nil` and need a full reset) | ✅ Released | v2.18.2 | [HTND#38](https://github.com/HoosatNetwork/HTND/pull/38) |
| A storage error while accepting a transaction is reported as an error instead of being treated as a bad transaction | 🔀 Merged | 2.18.3 | [HTND#57](https://github.com/HoosatNetwork/HTND/pull/57) |
| With the optional LevelDB database, a read error part-way through a walk over stored data is reported instead of the walk looking complete | 🔀 Merged | 2.18.3 | [HTND#76](https://github.com/HoosatNetwork/HTND/pull/76) ([HTND#69](https://github.com/HoosatNetwork/HTND/issues/69)) |
| The database's on-disk format is pinned, so a routine library update cannot leave older node versions unable to open the data | 🔄 In review | — | [HTND#73](https://github.com/HoosatNetwork/HTND/pull/73) ([HTND#70](https://github.com/HoosatNetwork/HTND/issues/70)) |
| The database keeps fewer files open than the process is allowed, leaving room for peer connections and logs | 🔄 In review | — | [HTND#74](https://github.com/HoosatNetwork/HTND/pull/74) ([HTND#71](https://github.com/HoosatNetwork/HTND/issues/71)) |
| The node logs its effective database settings at start and a short storage health summary while it runs | 🔄 In review | — | [HTND#75](https://github.com/HoosatNetwork/HTND/pull/75) ([HTND#72](https://github.com/HoosatNetwork/HTND/issues/72)) |
| When the database is found corrupt at start, keep diagnostics instead of silently deleting everything and re-syncing | 📝 Proposed | — | [HTN-03](findings/HTN-03.md), [HTN-43](findings/HTN-43.md) |

<details>
<summary>Technical details: data safety</summary>

- [HTN-02](findings/HTN-02.md): `updatePruningPoint` committed the deletion of past blocks before clearing the
  `updatingPruningPointUTXOSet` flag; a crash in that window left the flag set with the data gone. The fix clears the
  flag in the same batch as the deletion. Reproduced by `TestS2ResumeAfterDeletionCommitted` on both test-network
  configurations; merged as `8b666d5af`.
- [HTN-03](findings/HTN-03.md) and [HTN-43](findings/HTN-43.md) are drafts after an adversarial review found
  blockers (lock failure must fail closed, no deletion-in-place fallback, the evidence bundle is best-effort
  diagnostics). The cause of our own past corruption is unknown: [reports/db-recovery.md](reports/db-recovery.md).
- Related, not yet sent: [HTN-07](findings/HTN-07.md) (`Fatalf` returns instead of terminating),
  [HTN-26](findings/HTN-26.md) (WAL can be disabled by environment variables without a log line),
  [HTN-27](findings/HTN-27.md) (no bounded sync point for acknowledged writes).
- Database review, October 2026: four small changes, each sent after its own issue. #76: `Close()` on a LevelDB
  cursor now returns the iterator's error; with an injected read error the old code produced both a false mismatch
  and a partial set that happened to match (the default Pebble back end already returned the error). #73: the format
  is fixed at version 24, which current nodes already use, so existing data does not change. #74: the default file
  allowance (40,860) was far above the process limit the node sets (2,048); not seen failing, found in review. #75:
  also corrects two option comments that disagreed with the code. None changes consensus or the network protocol.

</details>

## 3. Memory

| What changed | Status | Version | Link |
|---|---|---|---|
| Three caches that were allocated but never read are removed: 342.9 MB less per node | ✅ Released | v2.18.2 | [HTND#39](https://github.com/HoosatNetwork/HTND/pull/39) |
| The database block cache is released when the database is closed | ✅ Released | v2.18.2 | [HTND#44](https://github.com/HoosatNetwork/HTND/pull/44) |
| The default memory limit is applied when `GOMEMLIMIT` is set but empty | 🔀 Merged | 2.18.3 | [HTND#43](https://github.com/HoosatNetwork/HTND/pull/43) |
| Derive the memory budget from the machine's RAM instead of fixed defaults that do not fit an 8 GB machine | 📝 Proposed | — | [HTN-17](findings/HTN-17.md) |

<details>
<summary>Technical details: memory</summary>

- [HTN-08](findings/HTN-08.md): three unused GHOSTDAG manager caches preallocated 342.9 MB per node; merged as
  `1349729f8`. #44 merged as `9cf3e87d6`.
- [reports/memory-test.md](reports/memory-test.md): two identical nodes, about 10.6 hours without a cap and 10.6 hours
  under a 7 GiB cap with default settings; three OOM kills under the cap, each followed by an automatic restart. The
  pruning-point move is the memory peak. The v2.18.2 release notes describe an experimental low-memory configuration
  (`GOMEMLIMIT`, smaller caches); we have not measured it.
- [HTN-17](findings/HTN-17.md): configured default budgets (Go soft limit 8.0 GB, Pebble cache 2 GiB, serialized
  caches 256/128 MiB) exceed an 8 GB host before any measured occupancy.

</details>

## 4. Sync and network

| What changed | Status | Version | Link |
|---|---|---|---|
| The block that moves the pruning point is passed on to peers before the node's own long clean-up, so the pause no longer piles up from node to node | ✅ Released | v2.18.2 | [HTND#47](https://github.com/HoosatNetwork/HTND/pull/47) |
| The longest part of that clean-up, checking the new UTXO set against its commitment, runs without stopping block processing; on a private test network the longest pause per move fell from 8.4–9.5 s to 0.6–1.7 s | 🔀 Merged | 2.18.3 | [HTND#77](https://github.com/HoosatNetwork/HTND/pull/77) ([HTND#41](https://github.com/HoosatNetwork/HTND/issues/41)) |
| Writing the new UTXO set still pauses block processing; proposal to move that out as well, after the change above | 🔄 In review | — | [HTND#42](https://github.com/HoosatNetwork/HTND/issues/42) |
| Proposal: measure how long each part of the node holds and waits for its main lock, with a warning when a hold is long | 🔄 In review | — | [HTND#68](https://github.com/HoosatNetwork/HTND/issues/68) |
| Proposal: the new RPC allow list keeps an operator's own RPC listener, and wildcard listeners keep accepting both IPv4 and IPv6 as before | 🔄 In review | — | [HTND#80](https://github.com/HoosatNetwork/HTND/issues/80) |
| A block whose parents arrive while it is being checked is processed instead of triggering a small re-sync | 🔀 Merged | 2.18.3 | [HTND#61](https://github.com/HoosatNetwork/HTND/pull/61) |
| The GetBlocks call no longer lists one block twice in its answer | 🔀 Merged | 2.18.3 | [HTND#62](https://github.com/HoosatNetwork/HTND/pull/62) |
| A peer's reject message is kept at no more than 2 KiB in the node's error and log | 🔄 In review | — | [HTND#64](https://github.com/HoosatNetwork/HTND/pull/64) |
| A new block is no longer announced back to the peer that just sent it | 🔀 Merged | 2.18.3 | [HTND#65](https://github.com/HoosatNetwork/HTND/pull/65) |
| The `--enablebanning` switch is respected by the block-relay flow | 🔄 In review | — | [HTND#56](https://github.com/HoosatNetwork/HTND/pull/56) |
| A block with no transactions reports the zero hash as its merkle root | 🔀 Merged | 2.18.3 | [HTND#45](https://github.com/HoosatNetwork/HTND/pull/45) |

<details>
<summary>Technical details: sync and network</summary>

- [HTN-39](findings/HTN-39.md): the relay flow announced the moving block only after the node's own pruning-point
  UTXO set update, so stalls cascaded hop by hop (on three of our nodes: 2–4 minutes per node, up to about 6 minutes
  across the three). Merged as `38a586e04` after review changes; the update normally runs after the announcement, with
  documented exceptions where a reader runs it first.
- [HTN-40](findings/HTN-40.md): the UTXO commitment scan (about 20.7 M entries on mainnet) runs under the consensus
  lock. On our nodes on v2.18.2 the pause per node is about 2–6 minutes; every node pauses at the same move. Not a
  regression, but the release does not remove the per-node pause on 8 GB machines.
- [HTND#77](https://github.com/HoosatNetwork/HTND/pull/77) follows the approach the Hoosat developers chose in
  #41: the full check still runs at every move, but on a fixed view of the data without the lock; a mismatch stops the
  node cleanly with a short diagnostic; a check overtaken by a newer pruning point is dropped with one loud warning.
  Side-by-side test on a private network, same server and load for both builds, test settings that move the pruning
  point about every 3 minutes, two rounds of 12 moves at about 1.27 million UTXO entries: lock held per move 8.4–9.5 s
  before, 0.66–1.58 s after; the check itself takes 9.5–9.8 s, now outside the lock. Fault drills (corrupted set,
  hard kill or stop during the check, three moves of downtime) behaved as designed. The remaining lock time is mostly
  writing the set (#42). Mainnet nodes hold about 16 times more entries; testnet comparison is the next step. Depends
  on #76.
- [HTND#61](https://github.com/HoosatNetwork/HTND/pull/61): on the public testnet one node started 69 small IBDs
  in a 35-minute window, 62 of them re-downloading blocks it already held as orphans; the trigger is a relayed block
  whose parents arrive during the orphan check. Side-by-side test on a private five-node network: 6.6 mini-IBDs per node-hour without the fix, 0 with it; relay p99 0.48 s against
  0.48–1.16 s; CPU equal. A wider orphan-resolution range was tested as an alternative and performed worse (higher relay
  p99, more red blocks), so it is not proposed.
- Figure: one pruning-point move on nodes A, B and C.

![Two-panel chart. Panel a: timeline of one pruning-point move on nodes A, B and C. Node C updates for 125 s; nodes A and B process no blocks until about 108 s, then run their own updates until 351 s and 315 s. Panel b: update phases per node without a cap and under a 7 GiB cap.](figures/pp-move-cascade.svg)

</details>

## 5. Mining and the bridge

| What changed | Status | Version | Link |
|---|---|---|---|
| Node: the Hoohash proof-of-work check gives the same result on every CPU; builds where the compiler fuses multiply-add (Apple silicon, `GOAMD64>=v3`) no longer reject valid blocks | 🔀 Merged | 2.18.3 | [HTND#35](https://github.com/HoosatNetwork/HTND/pull/35) |
| Bridge: the same proof-of-work fix for the bridge's own check | 🔀 Merged | 1.8.2 | [bridge#10](https://github.com/HoosatNetwork/htn-stratum-bridge/pull/10) |
| Bridge: miners get a fresh job as soon as the node announces a new block, instead of a cached one built on old tips | 🔀 Merged | 1.8.2 | [bridge#9](https://github.com/HoosatNetwork/htn-stratum-bridge/pull/9) |
| Bridge: job slots are not overwritten while a miner may still submit to them; job ids are allocated under a lock | 🔀 Merged | 1.8.2 | [bridge#12](https://github.com/HoosatNetwork/htn-stratum-bridge/pull/12) |
| Bridge: stratum lines that arrive in pieces are reassembled correctly, with a fixed line limit | 🔄 In review | — | [bridge#11](https://github.com/HoosatNetwork/htn-stratum-bridge/pull/11) |
| Bridge: a header-serialization test is checked against the node's own hash (the test had a stale expected value) | 🔀 Merged | 1.8.2 | [bridge#13](https://github.com/HoosatNetwork/htn-stratum-bridge/pull/13) |

<details>
<summary>Technical details: mining and bridge</summary>

- [HTN-01](findings/HTN-01.md): an unpatched darwin/arm64 build rejected 101/183 real mainnet blocks in the tested
  sample; amd64 (`GOAMD64=v1`) and the patched arm64 build accepted 183/183. The Hoosat developers confirmed the macOS
  case and plan a fix. linux/arm64 and `GOAMD64=v3` are inferred from compiler rules and disassembly, not executed.
- [HTN-44](findings/HTN-44.md): a pre-registered before/after on one solo bridge: own blocks missing a tip the node
  already knew fell from 46.7 % to 8.5 %. The effect on red blocks is not significant under the pre-registered test;
  only the mechanism (stale templates) is claimed.
- [HTN-20](findings/HTN-20.md): job slots were overwritten without an ownership check.
- Not yet sent: [HTN-31](findings/HTN-31.md) (block counters count every pool share), [HTN-32](findings/HTN-32.md)
  (shared tip blue score read and written without synchronisation).

![Grouped bar chart: PoW verdict on 183 real mainnet blocks. Unpatched darwin/arm64 build: 82 valid, 101 invalid; amd64 v1: 183 valid; patched darwin/arm64: 183 valid.](figures/pow-fma-arm64.svg)

</details>

## 6. Tests and tooling

| What changed | Status | Version | Link |
|---|---|---|---|
| A pruning test reads the pruning-point UTXOs with a bounded limit; the unbounded version ran out of memory on an 8 GB machine and took the rest of the test run with it | 🔀 Merged | 2.18.3 | [HTND#60](https://github.com/HoosatNetwork/HTND/pull/60) |
| The script builder writes a single zero byte as data instead of as an empty value | 🔄 In review | — | [HTND#63](https://github.com/HoosatNetwork/HTND/pull/63) |
| The script builder no longer crashes when asked for a zero lock time or sequence number | 🔀 Merged | 2.18.3 | [HTND#67](https://github.com/HoosatNetwork/HTND/pull/67) |
| The wallet daemon stops with an error when it cannot get the node's DAG information at start, instead of exiting silently | 🔀 Merged | 2.18.3 | [HTND#66](https://github.com/HoosatNetwork/HTND/pull/66) |
| Opt-in shutdown stress harness (see area 1) | 🔄 In review | — | [HTND#55](https://github.com/HoosatNetwork/HTND/pull/55) |
| Run more of the unit tests on every push, on every release architecture | 📝 Proposed | — | [HTN-19](findings/HTN-19.md), [HTN-24](findings/HTN-24.md), [HTN-25](findings/HTN-25.md), [HTN-34](findings/HTN-34.md) |

## Proposed, not yet sent

Written up with evidence and a recommendation, waiting their turn or the Hoosat developers' view. Severity and evidence level
for each are in [FINDINGS.md](FINDINGS.md).

<details>
<summary>All proposed items (30)</summary>

| Area | Item |
|---|---|
| Data safety | [HTN-03](findings/HTN-03.md) keep evidence on corruption (rework required) · [HTN-07](findings/HTN-07.md) `Fatalf` must not return · [HTN-26](findings/HTN-26.md) log when the WAL is disabled · [HTN-27](findings/HTN-27.md) bounded sync point · [HTN-43](findings/HTN-43.md) point-in-time WAL cut (prototype, not ready) |
| Availability | [HTN-11](findings/HTN-11.md) a failed pruning update must not livelock · [HTN-09](findings/HTN-09.md) difficulty computed twice per relayed block |
| Memory | [HTN-17](findings/HTN-17.md) memory budget from host RAM |
| Consensus (study, version-gated, testnet first) | [HTN-04](findings/HTN-04.md) GHOSTDAG K equals the parent count · [HTN-16](findings/HTN-16.md) deterministic FP64 PoW · [HTN-18](findings/HTN-18.md) ML-DSA-44 readiness · [HTN-29](findings/HTN-29.md) storage mass for UTXO growth · [HTN-15](findings/HTN-15.md) PoW-hash transport field |
| Process and docs | [HTN-13](findings/HTN-13.md) testnet on the current release · [HTN-14](findings/HTN-14.md) hard-fork lead time · [HTN-28](findings/HTN-28.md) release authentication · [HTN-33](findings/HTN-33.md) supply audit · [HTN-36](findings/HTN-36.md), [HTN-37](findings/HTN-37.md), [HTN-38](findings/HTN-38.md) documentation matches the code · [HTN-42](findings/HTN-42.md) install script line endings |
| Tests and CI | [HTN-19](findings/HTN-19.md) · [HTN-21](findings/HTN-21.md) · [HTN-24](findings/HTN-24.md) · [HTN-25](findings/HTN-25.md) · [HTN-34](findings/HTN-34.md) |
| Wallet and bridge | [HTN-23](findings/HTN-23.md) ML-DSA destinations before activation · [HTN-30](findings/HTN-30.md) default address type · [HTN-31](findings/HTN-31.md) · [HTN-32](findings/HTN-32.md) |

</details>

Security-sensitive findings are reported privately to the Hoosat developers and are not described here until a fix is
released ([SECURITY.md](SECURITY.md)).

*AI disclosure: prepared with AI assistance (Claude by Anthropic; cross-reviewed with OpenAI Codex).*
