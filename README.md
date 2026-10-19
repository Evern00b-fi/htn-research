# Making Hoosat nodes more reliable

We run Hoosat (HTN) nodes and a small mining setup. This project looks for things that make the Hoosat full node
(HTND) and the mining bridge crash, stall or lose data, and turns each one into a small fix that the Hoosat
developers can accept or reject on its own. The Hoosat developers decide what goes into a release; nothing here changes the chain's rules.

**Status marks**

| Mark | Meaning |
|---|---|
| ✅ Released | In a public Hoosat release; you get it by updating |
| 🔀 Merged | Accepted by the Hoosat developers; ships in the next release |
| 🔄 In review | Sent to the Hoosat developers; waiting for their decision |
| 🧪 Being tested | Fix written; being measured before it is sent |
| 📝 Proposed | Written up here; not yet sent |

## What is better now

All of these are in **HTND v2.18.2** (released 16 October 2026). Update your node to get them.

**Stability and clean shutdowns**

- ✅ Released in v2.18.2 — Stopping a busy node no longer crashes it with a "database closed" error. The node now waits
  for its ongoing work before closing the database, and exits without touching it if that takes too long.
- ✅ Released in v2.18.2 — Stopping a node no longer hangs when a peer connects at the wrong moment.

**Safety of your node's data**

- ✅ Released in v2.18.2 — A crash or kill during the regular "pruning" clean-up no longer leaves the node unable to
  start. Before, the only cure was a full reset and re-download.

**Memory**

- ✅ Released in v2.18.2 — Each node uses 342.9 MB less memory (three caches that were allocated but never read are gone),
  and the database cache is freed properly at shutdown.

**Sync and network**

- ✅ Released in v2.18.2 — When a block moves the pruning point (every few hours), the node now passes it on to its
  peers before doing its own long clean-up. Before, the pause piled up from node to node across the network. Each
  node's own pause still exists; see below.

Earlier releases and every change in detail: [CHANGES.md](CHANGES.md#by-release).

## What we are working on

- 🔀 Merged, in the next release — **The pruning pause.** Every few hours each node stops processing blocks for minutes while it rebuilds
  its pruning data; on our nodes running v2.18.2 about 2–6 minutes per node. The fix for the longest part, the check of
  the new data against its commitment, now runs without stopping block processing
  ([#77](https://github.com/HoosatNetwork/HTND/pull/77), the approach the Hoosat developers chose in
  [#41](https://github.com/HoosatNetwork/HTND/issues/41)). On a private test network the longest pause per move fell
  from 8.4–9.5 s to 0.6–1.7 s; mainnet holds about 16 times more data, so testnet comes next. Writing the data still
  pauses ([#42](https://github.com/HoosatNetwork/HTND/issues/42)).
- 🔀 / 🔄 **Database care.** Four small changes, each after its own issue (the first merged, three in review): a read error during a walk over
  stored data is no longer silently treated as the end, the on-disk format cannot change by accident in a library
  update, the database keeps within the open-file limit, and the node logs its storage health
  ([#73](https://github.com/HoosatNetwork/HTND/pull/73)–[#76](https://github.com/HoosatNetwork/HTND/pull/76)).
- 🔀 Merged, in the next release — **Fewer needless mini re-syncs.** A timing gap made a node start a small re-sync
  when a block's parents arrived while it was being checked. In a side-by-side test on a private network the fix cut
  these from 6.6 per node per hour to 0 ([#61](https://github.com/HoosatNetwork/HTND/pull/61)).
- 🔀 Merged, in the next release — **Clean shutdown, part two.** Six of eight small fixes so the node stops cleanly
  every time: no writes after stop, no log panics, a matching timeout in the systemd guide
  ([#48](https://github.com/HoosatNetwork/HTND/pull/48)–[#53](https://github.com/HoosatNetwork/HTND/pull/53)); the
  auto-updater wait and the stress harness are still in review.
- 🔀 Merged, in the next release — **Same proof-of-work result on every CPU.** On Apple-silicon Macs (and some newer
  x86 builds) the compiler can fuse two floating-point steps, and the Hoohash check comes out different: an unpatched
  Mac build rejected 101/183 real mainnet blocks. The fix forbids that fusion
  ([#35](https://github.com/HoosatNetwork/HTND/pull/35), [bridge #10](https://github.com/HoosatNetwork/htn-stratum-bridge/pull/10)).
- 🔀 Merged, in the next bridge release — **Mining bridge.** Fresher jobs for miners right after a new block, safer
  job bookkeeping and a repaired test; sturdier line handling is still in review
  ([bridge #9–#13](https://github.com/HoosatNetwork/htn-stratum-bridge/pulls)).
- 🔀 / 🔄 **Smaller fixes:** memory-limit default, a storage error no longer treated as a bad transaction, GetBlocks
  without duplicates, no block announced back to its sender and test fixes are merged; the banning switch, a 2 KiB cap
  on reject messages and a script-builder fix are in review. Listed in [CHANGES.md](CHANGES.md).
- 🔄 In review — **Measuring the main lock.** A proposal to log how long each part of the node holds and waits for its
  main lock ([#68](https://github.com/HoosatNetwork/HTND/issues/68)), so slowdowns can be traced to a cause.
- 📝 Proposed — Keep evidence instead of deleting the database when it is found corrupt; a memory budget that
  follows the machine's RAM; a study of the GHOSTDAG K parameter; and about 30 smaller items. See
  [CHANGES.md](CHANGES.md#proposed-not-yet-sent).

## How we test

Every fix comes with a test that fails before the change and passes after it. Bigger changes are also compared "with"
and "without" side by side on a throw-away private network. Every new HTND build from the Hoosat developers runs on
the public Hoosat testnet, and our tests are re-run on it to see which problems are fixed and which remain. Our own measurements are published without anything that identifies our machines: machine class, relative
times, aggregates. More in [METHODOLOGY.md](METHODOLOGY.md).

## For developers

| Page | Contents |
|---|---|
| [CHANGES.md](CHANGES.md) | Every change by area: status, version, link, technical details |
| [FINDINGS.md](FINDINGS.md) | The full record: 41 findings with severity, evidence level, chain impact and upstream status |
| [findings/](findings/) | One file per finding: affected code, evidence, recommendation, verification |
| [METHODOLOGY.md](METHODOLOGY.md) | How findings are checked, how fixes and builds are tested and compared, publication rules, limitations |
| [reports/](reports/) | Measurements: [red blocks](reports/red-blocks.md), [memory test](reports/memory-test.md), [database recovery](reports/db-recovery.md), [IBD timing](reports/ibd-timing.md), [testnet state](reports/testnet-state.md), [the first study](reports/first-study-2026-10.md) |
| [figures/](figures/README.md) | Charts and how to regenerate them |
| [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md) | Corrections welcome here; code changes belong upstream; how to report a vulnerability |

Upstream repositories: [HoosatNetwork/HTND](https://github.com/HoosatNetwork/HTND) and
[HoosatNetwork/htn-stratum-bridge](https://github.com/HoosatNetwork/htn-stratum-bridge). Discussion: the Hoosat
[Discord](https://discord.gg/EE5ZcTeuj) (Development category: `#node`, `#miners`, `#research`).

<details>
<summary>About this project</summary>

The work began in October 2026 as a reliability review of HTND 2.18.1 (branch `v2.18.1`, commit `a56566e86`) and
htn-stratum-bridge v1.8.0 (`3b2cf8c`) and continues with every new release. Fixes are sent against the Hoosat
developers' current development branch. Comparison baselines: kaspad `88bd604397`, rusty-kaspa `01b532e8b5`. Each pull
request addresses exactly one finding and carries its own test, as agreed with the Hoosat developers. Security-sensitive
findings are reported privately and are not described here until a fix is released.

Text and figures: [CC BY 4.0](LICENSE-docs.md). Scripts: [ISC](LICENSE), matching HTND's own licence. Corrections to this
repository are welcome ([CONTRIBUTING.md](CONTRIBUTING.md)); code changes and bug reports belong in the Hoosat
repositories.

**AI disclosure:** prepared with AI assistance (Claude by Anthropic; cross-reviewed with OpenAI Codex). Tests were run as
described.

</details>
