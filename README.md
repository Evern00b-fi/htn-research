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

The latest releases are **HTND v2.19.1** (17 November 2026) and **htn-stratum-bridge v1.9.0** (8 November 2026).
Update your node and your bridge to get these changes. Two more wallet fixes are merged into the 2.19.2 branch and ship
with the next HTND release; they are listed under the next heading.

**Mining**

- ✅ Released in bridge v1.9.0 — Miners get a fresh job as soon as the node announces a new block, instead of a stored
  one built on older blocks. On one solo bridge, own blocks missing a block the node already knew fell from 46.7 % to
  8.5 %.
- ✅ Released in bridge v1.9.0 — A job is no longer replaced while a miner may still send results for it.
- ✅ Released in bridge v1.9.0 — The bridge checks proof of work the same way on every CPU, as the node does since
  v2.18.3. Before, an unpatched Mac build rejected 101/183 real mainnet blocks.
- ✅ Released in v2.19.0 — After the node restarts, a connected mining bridge (or any other program using the node's
  RPC) is signed up for its notifications again automatically, so miners keep getting new jobs.

**Wallet**

- ✅ Released in v2.19.1 — htnwallet pays at least the minimum relay fee for a transaction's size, so heavy ML-DSA
  multisig spends are not rejected by nodes ([#113](https://github.com/HoosatNetwork/HTND/pull/113)).

**Running a node**

- ✅ Released in v2.19.1 — **A node that keeps running.** A local error while a peer connects (for example a database
  error) now disconnects that peer instead of stopping the whole node
  ([#110](https://github.com/HoosatNetwork/HTND/pull/110)). A chain-changed notification that refers to blocks removed
  after a sync is skipped with a warning instead of stopping the node
  ([#111](https://github.com/HoosatNetwork/HTND/pull/111)).
- ✅ Released in v2.19.1 — **Less memory and work per block.** The database releases each write batch right after it
  is saved, so the memory is reused instead of waiting for garbage collection
  ([#109](https://github.com/HoosatNetwork/HTND/pull/109)). The list of changed coins is prepared only when a client
  has subscribed to it, so no work is spent on it after every block when nobody listens
  ([#112](https://github.com/HoosatNetwork/HTND/pull/112)).
- ✅ Released in v2.19.1 — A node started with the write-ahead log turned off (test mode) starts again
  ([#107](https://github.com/HoosatNetwork/HTND/pull/107)), and two tests that failed on Windows or macOS pass again
  ([#108](https://github.com/HoosatNetwork/HTND/pull/108), [#114](https://github.com/HoosatNetwork/HTND/pull/114)).
- ✅ Released in v2.19.0 — The node logs the memory limit and garbage-collector setting it actually runs with, in the
  log file as well as on screen.
- ✅ Released in v2.19.0 — Once the ML-DSA signature upgrade is active, the mempool also counts ML-DSA signature
  checks toward its standardness limit for P2SH inputs, as it already does for the older signature checks.

Earlier releases (v2.18.3: a shorter pruning pause, no needless mini re-syncs, cleaner shutdowns, the same
proof-of-work result on every CPU, a storage health summary in the log and smaller fixes; v2.18.2: no crash when
stopping a busy node, a safe pruning clean-up, 342.9 MB less memory per node) and every change in detail:
[CHANGES.md](CHANGES.md#by-release).

## What we are working on

- 🔀 Merged into 2.19.2 — **Lighter wallet syncing.** The wallet daemon no longer asks its node about every used
  address every 2 seconds: after the first full scan it checks the addresses near the last used ones on every sync and
  the older ones a batch at a time ([#120](https://github.com/HoosatNetwork/HTND/pull/120)). A burst of sends now
  leads to one extra sync instead of one per send ([#121](https://github.com/HoosatNetwork/HTND/pull/121)).
- ✅ Released in v2.18.3, measurement next — **The pruning pause.** Every few hours each node stops processing blocks
  for minutes while it rebuilds its pruning data; on our nodes running v2.18.2 about 2–6 minutes per node. The check of
  the new data against its commitment, the longest part, now runs without stopping block processing
  ([#77](https://github.com/HoosatNetwork/HTND/pull/77), the approach the Hoosat developers chose in
  [#41](https://github.com/HoosatNetwork/HTND/issues/41)). On a private test network the longest pause per move fell
  from 8.4–9.5 s to 0.6–1.7 s; mainnet holds about 16 times more data, so testnet comes next. Writing the data is now
  split into small steps that resume after a crash, and old history is deleted in the background
  ([#82](https://github.com/HoosatNetwork/HTND/pull/82), from [#42](https://github.com/HoosatNetwork/HTND/issues/42));
  its effect on the pause is not measured yet.
- ✅ / 🔄 **Database care.** Released in v2.18.3: a read error during a walk over stored data is no longer silently
  treated as the end, and the node logs its storage health. In review: the on-disk format cannot change by accident in
  a library update, and the database keeps within the open-file limit
  ([#73](https://github.com/HoosatNetwork/HTND/pull/73), [#74](https://github.com/HoosatNetwork/HTND/pull/74)); and a
  proposal that a node with a damaged database names the likely cause (a power cut, or faulty memory or disk) and stops
  restarting in a loop ([#90](https://github.com/HoosatNetwork/HTND/issues/90)).
- ✅ / 🔄 **Clean shutdown, last part.** Six of eight small fixes are released in v2.18.3
  ([#48](https://github.com/HoosatNetwork/HTND/pull/48)–[#53](https://github.com/HoosatNetwork/HTND/pull/53)). A stop
  request that ends the wait before an automatic update install is in review
  ([#54](https://github.com/HoosatNetwork/HTND/pull/54)); the stress test stays in our own testing.
- 🔄 In review — **Mining bridge.** Sturdier handling of stratum lines that arrive in pieces, and the bridge signing up
  for new-template notifications again after a node restart, a full address kept when a worker name follows another
  separator, and an error reply for an invalid wallet address
  ([bridge #11](https://github.com/HoosatNetwork/htn-stratum-bridge/pull/11),
  [bridge #16](https://github.com/HoosatNetwork/htn-stratum-bridge/pull/16),
  [bridge #19](https://github.com/HoosatNetwork/htn-stratum-bridge/pull/19),
  [bridge #20](https://github.com/HoosatNetwork/htn-stratum-bridge/pull/20)).
- 🔀 Merged — **DNS seeder.** The seeder stops re-dialling addresses that never answer, keeps good nodes in its
  answers, and locks its address book while it counts addresses
  ([dnsseeder #1](https://github.com/HoosatNetwork/dnsseeder/pull/1),
  [dnsseeder #2](https://github.com/HoosatNetwork/dnsseeder/pull/2)).
- 🔄 In review — **Explorer.** The socket server keeps reading new blocks while it fetches block details, so it no
  longer falls behind and gets disconnected during catch-up; open explorer pages rejoin live updates after a reconnect
  ([htn-socket-server #1](https://github.com/HoosatNetwork/htn-socket-server/pull/1),
  [htn-explorer #12](https://github.com/HoosatNetwork/htn-explorer/pull/12)).
- 🔄 **Smaller fixes:** a script-builder fix
  ([#63](https://github.com/HoosatNetwork/HTND/pull/63)), a proposal to turn the full test suite back on in CI
  with a routine any contributor can follow ([#115](https://github.com/HoosatNetwork/HTND/issues/115)) and a proposal that a node already listening for RPC on its
  own address and the default port still starts with the new RPC allow list
  ([#80](https://github.com/HoosatNetwork/HTND/issues/80)) are in review. Closed by us: an opt-in, node-wide limit on
  address-index RPC requests ([#99](https://github.com/HoosatNetwork/HTND/issues/99)); our measured wallet load did not justify the
  option, and the comparison pointed to how the UTXO buffer is sized as the relevant cost. The separately tested buffer
  change (`0fa4041`) was reverted from 2.19.1; the Hoosat developers then merged the same buffer sizing in
  [#117](https://github.com/HoosatNetwork/HTND/pull/117).
- 📝 Proposed — Keep evidence instead of deleting the database when it is found corrupt; a memory budget that
  follows the machine's RAM; a study of the GHOSTDAG K parameter; 30 items in all. See
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
