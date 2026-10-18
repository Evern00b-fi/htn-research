# Findings

Scope: HTND `a56566e86` (branch v2.18.1) and htn-stratum-bridge v1.8.0 (`3b2cf8c`). IDs are stable; severities
were revised after review, so ID order is not severity order. Details per finding: `findings/HTN-xx.md`.
Gaps in the numbering are items withdrawn before publication; their IDs are not reused. HTN-39 to HTN-44 were added
after the first draft. **41 public findings: High 3, Medium 19, Low 13, Informational 6.**

The *Status* of HTN-03 and HTN-43 records the outcome of an adversarial review of their draft PRs. Status last
checked against GitHub on 2026-10-17: HTND pull requests 8 merged and released in v2.18.2, 15 open; HTND issues 2 open;
bridge pull requests 5 open; none closed or rejected.
Headline numbers: an unpatched darwin/arm64 build rejects 101/183 real mainnet blocks
(HTN-01); three unused caches hold 342.9 MB (HTN-08); at fixed topology K=18 changes the red share from 8.792 % to
1.120 %, and on a limit-consistent prefix from 9.622 % to 0.590 % (HTN-04); a pruning-point move stopped block
processing for 2–4 minutes per node and up to about 6 minutes across our three nodes (our log measurements;
HTN-39, HTN-40).

## Severity scale

| Severity | Criteria |
|---|---|
| Critical | Consensus split, fund loss or remote compromise on the default build and platform, exploitable now. |
| High | Node becomes unusable without a reset or resync; data or evidence is destroyed; consensus disagreement on a shipped build or platform; a security guarantee materially below its design. |
| Medium | Degraded availability or performance; unclean shutdown; latent consensus divergence that would appear at a future activation; significant resource waste; a process gap that lets regressions reach releases. |
| Low | Limited-impact correctness, policy or robustness issues. |
| Informational | Documentation, tooling or process observations with no direct runtime impact. |

## Evidence levels

| Level | Meaning |
|---|---|
| Reproduced | A test or reproducer fails at the pinned commit and (where a fix exists) passes after it; re-run at least twice, in most cases also by the independent second review. A qualifier in parentheses narrows what was reproduced. |
| Code-confirmed | The mechanism is established by reading the pinned code (and git history); no reproducer was run. |
| Measured | Observed or quantified in operational data (our own nodes, anonymised) or public network data. |
| Hypothesis | Plausible and partly supported, but the decisive observation is missing. Stated as such. |

Each finding's *Verification* section separates what is **Completed** from what is **Required before submission**.
Test names without public fixtures, patches and logs are not independently reproducible evidence; those artifacts
are published with the corresponding PR.

## Chain impact

**none** = node-local, no wire or validity change · **P2P version** = wire change; old and new nodes coexist until the
old version is retired · **version-gated forward fork** = rule change at a future DAA score; the chain keeps running
and non-upgraded nodes fork off. No finding requires halting, rewinding or reorganising the chain.

## Table

| ID | Title | Severity | Category | Evidence | Chain impact | Action | Status | Upstream |
|---|---|---|---|---|---|---|---|---|
| [HTN-01](findings/HTN-01.md) | Hoohash v1.1.0 PoW evaluates differently on builds where the compiler fuses multiply-add | High | consensus | Reproduced | none | PR | Merged 2026-10-17 into 2.18.3 (dd7bd9067) and bridge 1.8.2 (99f98500a) | PR [HTND#35](https://github.com/HoosatNetwork/HTND/pull/35), [bridge#10](https://github.com/HoosatNetwork/htn-stratum-bridge/pull/10) |
| [HTN-02](findings/HTN-02.md) | Pruning-point update deletes past blocks before clearing its in-progress flag | High | storage | Reproduced | none | PR | Merged 2026-10-13 into 2.18.2 (8b666d5af) — released in v2.18.2 (16 October 2026) | PR [HTND#38](https://github.com/HoosatNetwork/HTND/pull/38) |
| [HTN-03](findings/HTN-03.md) | Datadir is deleted on Pebble corruption at open; no evidence is kept | High | storage | Reproduced | none | PR | Draft — rework required (review found blockers: lock failure must fail closed, missing-parent regression, no deletion-in-place fallback, bundle is best-effort diagnostics, not a protected copy) | TBD |
| [HTN-04](findings/HTN-04.md) | GHOSTDAG K equals the block's parent count; a version-gated K floor should be studied | Medium | consensus | Reproduced (mechanism; operational security impact unverified) | version-gated forward fork | Issue | Draft — not yet submitted | TBD |
| [HTN-05](findings/HTN-05.md) | Database is closed under active users when graceful shutdown times out | Medium | availability | Measured | none | PR | Merged 2026-10-12 into 2.18.2 (c36ba8c3d) — released in v2.18.2 (16 October 2026) | PR [HTND#37](https://github.com/HoosatNetwork/HTND/pull/37) |
| [HTN-06](findings/HTN-06.md) | NetAdapter accepts new P2P connections while stopping; shutdown can hang | Medium | availability | Reproduced | none | PR | Merged 2026-10-12 into 2.18.2 (717a3366c) — released in v2.18.2 (16 October 2026) | PR [HTND#40](https://github.com/HoosatNetwork/HTND/pull/40) |
| [HTN-07](findings/HTN-07.md) | Pebble logger adapter: `Fatalf` returns instead of terminating | Medium | storage | Reproduced | none | PR | Draft — not yet submitted | TBD |
| [HTN-08](findings/HTN-08.md) | Three unused GHOSTDAG caches preallocate about 343 MB per node | Medium | memory | Reproduced | none | PR | Merged 2026-10-12 into 2.18.2 (1349729f8) — released in v2.18.2 (16 October 2026) | PR [HTND#39](https://github.com/HoosatNetwork/HTND/pull/39) |
| [HTN-09](findings/HTN-09.md) | Block relay recomputes required difficulty twice per block through `GetVirtualInfo` | Medium | performance | Measured | none | PR | Draft — not yet submitted | TBD |
| [HTN-11](findings/HTN-11.md) | A failed pruning-point UTXO update must not livelock the node | Medium | availability | Code-confirmed | none | Issue | Draft — not yet submitted | TBD |
| [HTN-13](findings/HTN-13.md) | Public testnet does not run the current release parameters | Medium | process | Measured | none | Issue | Draft — not yet submitted | TBD |
| [HTN-14](findings/HTN-14.md) | Hard-fork lead time and a testnet-first policy | Medium | process | Code-confirmed | none | Issue | Draft — not yet submitted | TBD |
| [HTN-15](findings/HTN-15.md) | Block acceptance in relay depends on a transport field the block hash does not commit to | Medium | P2P | Code-confirmed | none / P2P version | Issue | Draft — not yet submitted | TBD |
| [HTN-16](findings/HTN-16.md) | Deterministic FP64 PoW: keep ASIC resistance, remove platform dependence | Medium | consensus | Hypothesis | version-gated forward fork | Issue | Draft — not yet submitted | TBD |
| [HTN-17](findings/HTN-17.md) | Memory budget is not derived from host RAM | Medium | memory | Measured | none | Issue | Draft — not yet submitted | TBD |
| [HTN-18](findings/HTN-18.md) | ML-DSA-44 activation readiness | Medium | consensus | Code-confirmed | version-gated forward fork | Issue | Draft — not yet submitted | TBD |
| [HTN-19](findings/HTN-19.md) | Per-push CI runs almost no unit tests | Medium | process | Code-confirmed | none | PR | Draft — not yet submitted | TBD |
| [HTN-20](findings/HTN-20.md) | Bridge: job slots are overwritten without an ownership check | Medium | tooling | Reproduced | none | PR | Merged 2026-10-17 into 1.8.2 (2f5f25cc3) | PR [bridge#12](https://github.com/HoosatNetwork/htn-stratum-bridge/pull/12) |
| [HTN-21](findings/HTN-21.md) | Hard-fork gate tests pin stale constants; one would activate ML-DSA if "fixed" naively | Low | tooling | Reproduced | none | PR | Draft — not yet submitted | TBD |
| [HTN-23](findings/HTN-23.md) | Wallet and mempool accept ML-DSA destinations before activation | Medium | tooling | Code-confirmed | none | PR | Draft — not yet submitted | TBD |
| [HTN-24](findings/HTN-24.md) | CI does not run the PoW package on every release architecture | Low | tooling | Code-confirmed | none | PR | Draft — not yet submitted | TBD |
| [HTN-25](findings/HTN-25.md) | PoW build tags leave linux/arm64 without cgo uncovered | Low | tooling | Reproduced | none | PR | Draft — not yet submitted | TBD |
| [HTN-26](findings/HTN-26.md) | WAL can be disabled by environment variables without any log line | Low | storage | Reproduced | none | PR | Draft — not yet submitted | TBD |
| [HTN-27](findings/HTN-27.md) | Durability: no bounded sync point for acknowledged writes | Low | storage | Reproduced | none | Issue | Draft — not yet submitted | TBD |
| [HTN-28](findings/HTN-28.md) | Release authentication and updater verification need completion | Low | process | Code-confirmed | none | Issue | Draft — not yet submitted | TBD |
| [HTN-29](findings/HTN-29.md) | No storage mass (KIP-9 style) bounds UTXO-set growth | Low | consensus | Code-confirmed | version-gated forward fork | Issue | Draft — not yet submitted | TBD |
| [HTN-30](findings/HTN-30.md) | Default wallet address type is P2PK, exposing public keys at rest | Low | tooling | Code-confirmed | none | Issue | Draft — not yet submitted | TBD |
| [HTN-31](findings/HTN-31.md) | Bridge: block counters record every accepted pool share as a found block | Low | tooling | Reproduced | none | PR | Draft — not yet submitted | TBD |
| [HTN-32](findings/HTN-32.md) | Bridge: shared tip blue score is read and written without synchronisation | Low | tooling | Reproduced | none | PR | Draft — not yet submitted | TBD |
| [HTN-33](findings/HTN-33.md) | Supply integrity: publish the emission model and a reproducible supply audit | Informational | tooling | Documentation/tooling proposal; reconciliation unverified | none | Issue | Draft — not yet submitted | TBD |
| [HTN-34](findings/HTN-34.md) | CI toolchain pin disagrees with `go.mod` | Informational | tooling | Code-confirmed | none | PR | Draft — not yet submitted | TBD |
| [HTN-35](findings/HTN-35.md) | Docs: systemd unit in the node guide lacks `TimeoutStopSec` | Informational | docs | Code-confirmed | none | PR | Merged 2026-10-17 into 2.18.3 (474a1f2de) | PR [HTND#52](https://github.com/HoosatNetwork/HTND/pull/52) |
| [HTN-36](findings/HTN-36.md) | Docs: describe GHOSTDAG K as implemented rather than as DAGKnight | Informational | docs | Code-confirmed | none | PR | Draft — not yet submitted | TBD |
| [HTN-37](findings/HTN-37.md) | Docs: describe the PoW-hash check as implemented | Informational | docs | Code-confirmed | none | PR | Draft — not yet submitted | TBD |
| [HTN-38](findings/HTN-38.md) | Rationale for consensus parameters at 5 BPS is undocumented | Informational | docs | Code-confirmed | none | Issue | Draft — not yet submitted | TBD |
| [HTN-39](findings/HTN-39.md) | The block that moves the pruning point is relayed only after its UTXO update; stalls cascade hop by hop | Medium | availability | Measured | none | PR | Merged 2026-10-13 into 2.18.2 (38a586e04) — released in v2.18.2 (16 October 2026) | PR [HTND#47](https://github.com/HoosatNetwork/HTND/pull/47) |
| [HTN-40](findings/HTN-40.md) | The pruning-point UTXO commitment scan holds the consensus lock for minutes on every move | Medium | availability | Measured | none | Issue | Merged 2026-10-18 into 2.18.3 (a94e94058) as PR #77, the approach chosen in #41 | Issue [HTND#41](https://github.com/HoosatNetwork/HTND/issues/41), PR [HTND#77](https://github.com/HoosatNetwork/HTND/pull/77); follow-up [HTND#42](https://github.com/HoosatNetwork/HTND/issues/42) |
| [HTN-41](findings/HTN-41.md) | `ConnectionManager.Stop` can block forever on waking a connection loop that has already returned | Medium | availability | Reproduced | none | PR | Merged 2026-10-12 into 2.18.2 (5b1c9e3b6) — released in v2.18.2 (16 October 2026) | PR [HTND#36](https://github.com/HoosatNetwork/HTND/pull/36) |
| [HTN-42](findings/HTN-42.md) | Install script and sample systemd unit are stored with CRLF line endings; the script does not parse | Low | tooling | Reproduced | none | PR | Draft — not yet submitted | TBD |
| [HTN-43](findings/HTN-43.md) | A damaged record in an older WAL forces a full resync; a point-in-time WAL cut could avoid it (research) | Low | storage | Reproduced | none | PR | Prototype — not ready (review: transient read errors cause extra loss 364→243 keys; missing durability barrier; depends on the pruning-flag fix) | TBD |
| [HTN-44](findings/HTN-44.md) | Bridge: the template cache is no longer cleared on a new-block notification | Low | tooling | Measured | none | PR | Merged 2026-10-17 into 1.8.2 (6e4af6a5d) | PR [bridge#9](https://github.com/HoosatNetwork/htn-stratum-bridge/pull/9) |
| — | Security-related findings — not listed here. Reported privately to the maintainers; mechanics intentionally omitted; published only after a fix is released and disclosure is agreed. | — | — | — | none | private disclosure | Reported privately | — |

## Further submissions

Small fixes prepared after the findings table was fixed in scope; they are not separate findings (HTND#52 is HTN-35
and is listed in the table above).

| Pull request | Change | Status |
|---|---|---|
| [HTND#43](https://github.com/HoosatNetwork/HTND/pull/43) | Apply the default memory limit when `GOMEMLIMIT` is set but empty | Merged 2026-10-17 into 2.18.3 (9e77fd7dd) |
| [HTND#44](https://github.com/HoosatNetwork/HTND/pull/44) | Release the Pebble block cache when the database is closed | Merged 2026-10-13 (9cf3e87d6) — released in v2.18.2 (16 October 2026) |
| [HTND#45](https://github.com/HoosatNetwork/HTND/pull/45) | Return the zero hash as the merkle root of no transactions | Merged 2026-10-17 into 2.18.3 (bbe7da94e) |
| [bridge#11](https://github.com/HoosatNetwork/htn-stratum-bridge/pull/11) | Frame stratum lines across reads with a fixed line limit | Submitted 2026-10-12 — open |
| [bridge#13](https://github.com/HoosatNetwork/htn-stratum-bridge/pull/13) | Repair `TestHeaderSerialization` (stale expected hash) | Merged 2026-10-17 into 1.8.2 (ccc396a76) |
| [HTND#46](https://github.com/HoosatNetwork/HTND/pull/46) | Wait for running RPC handlers before closing the database on shutdown (builds on #37) | Merged 2026-10-13 (e6eb0bb82) — released in v2.18.2 (16 October 2026) |
| [HTND#48](https://github.com/HoosatNetwork/HTND/pull/48) | Count a protocol router in the wait group before spawning its flows goroutine (clean shutdown) | Merged 2026-10-17 into 2.18.3 (6a03e0c8f) |
| [HTND#49](https://github.com/HoosatNetwork/HTND/pull/49) | Wait for both handshake goroutines before the handshake returns (clean shutdown) | Merged 2026-10-17 into 2.18.3 (1369fabe5) |
| [HTND#50](https://github.com/HoosatNetwork/HTND/pull/50) | Stop address-manager database writes once the node has stopped (clean shutdown) | Merged 2026-10-17 into 2.18.3 (783f1900e) |
| [HTND#51](https://github.com/HoosatNetwork/HTND/pull/51) | Flush the memtables on close when the write-ahead log is disabled (clean shutdown) | Merged 2026-10-17 into 2.18.3 (b3c910522) |
| [HTND#53](https://github.com/HoosatNetwork/HTND/pull/53) | Write log lines made after Close to stderr instead of panicking (clean shutdown) | Merged 2026-10-17 into 2.18.3 (c720972a2) |
| [HTND#54](https://github.com/HoosatNetwork/HTND/pull/54) | Let Stop end the wait before an automatic update install (clean shutdown) | Submitted 2026-10-14 — open |
| [HTND#55](https://github.com/HoosatNetwork/HTND/pull/55) | Opt-in shutdown stress harness (test only; clean shutdown) | Submitted 2026-10-14 — open |
| [HTND#56](https://github.com/HoosatNetwork/HTND/pull/56) | Respect --enablebanning in relay-flow bans | Submitted 2026-10-14 — open |
| [HTND#57](https://github.com/HoosatNetwork/HTND/pull/57) | Treat a storage error during transaction acceptance as an error, not a rejection | Merged 2026-10-17 into 2.18.3 (e843cb378) |
| [HTND#60](https://github.com/HoosatNetwork/HTND/pull/60) | Test: read the pruning point UTXOs with a bounded limit (the test ran out of memory on an 8 GB machine) | Merged 2026-10-17 into 2.18.3 (222ab70f4) |
| [HTND#61](https://github.com/HoosatNetwork/HTND/pull/61) | Process a relayed block whose parents arrive during the orphan check (orphan-pool race behind the extra small IBDs; devnet A/B 6.6 -> 0 per node-hour) | Merged 2026-10-17 into 2.18.3 (eef308bd1) |
| [HTND#62](https://github.com/HoosatNetwork/HTND/pull/62) | GetBlocks lists the low hash only once | Merged 2026-10-17 into 2.18.3 (510126f09) |
| [HTND#63](https://github.com/HoosatNetwork/HTND/pull/63) | Script builder: a single zero byte is written as data | Submitted 2026-10-17 — open |
| [HTND#64](https://github.com/HoosatNetwork/HTND/pull/64) | Keep a peer's reject reason at no more than 2 KiB in errors and logs | Submitted 2026-10-17 — open |
| [HTND#65](https://github.com/HoosatNetwork/HTND/pull/65) | Do not announce a new block back to the peer that sent it | Merged 2026-10-17 into 2.18.3 (1099ee978) |
| [HTND#66](https://github.com/HoosatNetwork/HTND/pull/66) | Wallet daemon: stop with an error when the node's DAG information cannot be read at start | Merged 2026-10-17 into 2.18.3 (cc05c25b1) |
| [HTND#67](https://github.com/HoosatNetwork/HTND/pull/67) | Script builder: no crash on a zero lock time or sequence | Merged 2026-10-17 into 2.18.3 (32be8eb4b) |
| [HTND#73](https://github.com/HoosatNetwork/HTND/pull/73) | Pin Pebble's on-disk format to version 24 (issue #70) | Submitted 2026-10-18 — open |
| [HTND#74](https://github.com/HoosatNetwork/HTND/pull/74) | Budget Pebble's file cache against the process open-file limit (issue #71) | Submitted 2026-10-18 — open |
| [HTND#75](https://github.com/HoosatNetwork/HTND/pull/75) | Log effective Pebble options and compact storage metrics (issue #72) | Submitted 2026-10-18 — open |
| [HTND#76](https://github.com/HoosatNetwork/HTND/pull/76) | LevelDB cursor: return the iterator's error on Close (issue #69) | Merged 2026-10-18 into 2.18.3 (6d1f857b0) |

## Not included (not yet decision-ready)

- Orphan-resolution range tuned for 1 BPS (`orphanResolutionRange=5`): a wider range was tested side by side with the
  HTND#61 fix on a private network and performed worse (higher relay p99, more red blocks); not proposed.
- Five pruning-import / headers-proof tests failing at a56566e86: fixture drift or defect not yet classified (tracked under HTN-19).
- Dead GitHub panic-reporting code (token never set, opt-in flag has no effect).

_AI disclosure: prepared with AI assistance (Claude by Anthropic; cross-reviewed with OpenAI Codex)._
