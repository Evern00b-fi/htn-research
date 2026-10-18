# Red blocks on mainnet: measurement (R1), counterfactual re-colouring (R2) and timing (R3)

Related findings: [HTN-04](../findings/HTN-04.md), [HTN-40](../findings/HTN-40.md), [HTN-44](../findings/HTN-44.md).
R1 and R2 use a single node's recorded view of the mainnet DAG (HTND 2.18.1-a56566e86, `GetBlocks` verbose RPC) over a
window of about 9 hours on one day in October 2026. They observe neither block propagation nor miner intent, and
neither predicts the red rate after any rule change. R3 adds first-seen times from three nodes and a later window.

## R1 — how many blocks are red today

Data: 165,427 blocks. Colouring is taken from the merge sets of selected-chain blocks, which partition the DAG, so each
block is coloured once (blue ∩ red = 0). "Miner" is the first coinbase output script, anonymised; coinbase outputs pay
merged ancestors, so these groups do **not** necessarily identify the producing miner.

| Metric | Value |
|---|---|
| Selected-chain blocks | 67,353 (40.7 % of all) |
| Red share of all blocks | **8.71 %** (14,407) |
| Red share of parallel blocks (selected parents excluded) | **14.69 %** |
| Merged parallel blocks per chain block (mean) | 1.46 |
| Parent count (= dynamic K) | 1: 23.7 %, 2: 35.1 %, 3: 25.5 %, 4: 11.2 %, 5+: 4.5 % |
| Hourly red share | 5.1–10.7 % |

| Group (anon.) | Share of blocks | Red |
|---|---|---|
| #A | 32.5 % | 6.5 % |
| #B | 24.0 % | 11.5 % |
| #C | 20.3 % | 7.0 % |
| #D | 8.0 % | 8.9 % |
| #E | 3.9 % | 14.5 % |
| #F | 3.6 % | 11.3 % |

![Bar chart: share of blocks by number of parents, which equals the K applied to the block. 1 parent 23.7 %, 2 parents 35.1 %, 3 parents 25.5 %, 4 parents 11.2 %, 5 or more 4.5 %.](../figures/parent-count-distribution.svg)

Observations (hypotheses, not conclusions): almost half of all blocks are off the selected chain, so parallelism at
5 BPS is high; with K equal to the parent count (often 1–2) even modest extra parallelism colours blocks red. Groups
differ by about 2x in red share, which points at propagation delay or template freshness as well as the rule. A public
dashboard's "~9 %" figure agrees with the 8.71 % measured here.

## R2 — what the same DAG looks like under other K rules

**Validation first.** A standalone, standard-library Go replay of HTND's GHOSTDAG (`ghostdag.go`, `mergeset.go`,
`compare.go`: highest cumulative blue work, lexicographically largest hash on ties, mergeset ordering, blue-count cap
K+1, the v7+ anticone bound and the exact `4*K` max-walk cutoff) matches the node exactly for all 160,427 blocks after
a 5,000-block warm-up: selected parent, blue set, red set, ordered blue and red lists and recorded selected-chain
membership all agree 100 %. Four blocks disagree before warm-up because four parent hashes are missing from the window
and are collapsed to a zero-work virtual genesis. Node colours were used only for validation, never to seed the replay.

**Population.** 160,327 blocks (the first 5,000 and last 100 excluded for warm-up and tip censoring). Each variant
selects its own highest-work endpoint and follows its own selected-parent chain; chain merge sets assign each block one
colour. Supplied difficulties and block versions are kept fixed; all blocks are version 10.

| K rule | Reds | All red % | Off-chain red % | Chain length | Chain removed/added vs baseline |
|---|---:|---:|---:|---:|---:|
| Parents (today) | 14,096 | 8.792 | 14.817 | 65,193 | 0/0 |
| 3 | 17,701 | 11.041 | 18.738 | 65,863 | 2,841/3,511 |
| 5 | 7,268 | 4.533 | 7.711 | 66,072 | 2,800/3,679 |
| 8 | 3,560 | 2.220 | 3.783 | 66,221 | 2,731/3,759 |
| 11 | 2,614 | 1.630 | 2.777 | 66,181 | 2,889/3,877 |
| 18 | 1,795 | 1.120 | 1.907 | 66,203 | 2,865/3,875 |
| 40 | 1,309 | 0.816 | 1.392 | 66,275 | 2,728/3,810 |
| max(P,11) | 2,609 | 1.627 | 2.771 | 66,181 | 2,888/3,876 |
| max(P,18) | 1,795 | 1.120 | 1.907 | 66,203 | 2,865/3,875 |

![Bar chart: red share of all blocks per K rule on the same recorded DAG. Parents (today) 8.792 %, K=3 11.041 %, K=5 4.533 %, K=8 2.220 %, K=11 1.630 %, K=18 1.120 %, K=40 0.816 %.](../figures/red-blocks-by-k.svg)

At fixed topology, K=18 changes the red share from **8.792 % to 1.120 %** (12,343 original reds become blue, 42 original
blues become red). About 4.4 % of baseline chain members leave the chain and 3,875 blocks enter it. Fixed K=3 *increases*
reds: it lowers K for wider blocks, and neither chain selection nor colouring is monotone under that change.

**The 180-block merge-set limit.** The limit is a validity check, not a truncation rule. The full-window replays retain
every edge and record violations: fixed K=3/5/8/11/18/40 produce 35/27/21/17/**11**/6 oversized merge sets (maximum
332). None is itself a selected-chain block, but roughly 69–70 thousand cohort blocks are these blocks or their
descendants. **These full-window variants are therefore not executable consensus histories with the limit retained.**
Strict mode rejects them; K=3 first fails at block 92,335.

Replaying only the first 90,000 blocks with strict enforcement gives an 84,900-block cohort and **zero violations for
every variant**:

| K rule | Parents | 3 | 5 | 8 | 11 | 18 | 40 | max(P,11) | max(P,18) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| All red % | 9.622 | 11.502 | 4.663 | 1.988 | 1.304 | 0.590 | 0.210 | 1.299 | 0.590 |

Here K=18 changes the red share from **9.622 % to 0.590 %**. This shows that the reduction does not depend on exceeding
the merge-set limit, although it is a different time window.

**Per-group rates** (first coinbase output as proxy; the same six leading groups as R1; red % under each rule):

| Group | Share % | Parents | 5 | 11 | 18 | 40 |
|---|---:|---:|---:|---:|---:|---:|
| #A | 32.4 | 6.53 | 2.92 | 0.50 | 0.19 | 0.08 |
| #B | 24.1 | 11.61 | 5.87 | 2.22 | 1.35 | 0.65 |
| #C | 20.2 | 7.10 | 3.25 | 0.68 | 0.33 | 0.19 |
| #D | 8.0 | 8.85 | 4.64 | 2.02 | 1.39 | 1.16 |
| #E | 3.9 | 14.67 | 10.27 | 5.33 | 4.16 | 3.29 |
| #F | 3.7 | 11.32 | 8.16 | 5.76 | 5.44 | 5.19 |

Differences between groups persist at K=18, so something other than the rule (delay, template age) also matters.

## What R2 does and does not show

- It shows that, with the recorded topology frozen, a higher K would have coloured far fewer blocks red, and that the
  reduction holds on a limit-consistent prefix.
- It does **not** show that "most reds are caused by K rather than topology": the experiment cannot separate the
  causal shares of the K rule, topology and propagation delay. The remaining 1.12 % (0.82 % at K=40) is topology
  interacting with finite K and HTND's other colouring rules, not an irreducible topology-only fraction.
- It does **not** predict live red rates after a rule change: a live K change alters parents, templates, difficulty,
  hashes and miner behaviour, all of which are frozen here. Changed colours also invalidate existing header
  commitments, so even the limit-consistent prefix is a structural experiment, not a replay of unchanged consensus blocks.
- It does **not** establish an attack threshold. Block-count red rates are not a difficulty-weighted adversarial
  measure; the simplified `b/(1+b)` model figure quoted internally is not a measurement.
- Warm-up sensitivity: excluding 100–20,000 blocks gives K=18 net reductions of 86.4–87.5 %.

## R3 — what goes with red blocks: arrival delay, missed tips and pruning-point moves

R2 left a question open: groups differ in red share even at K=18. R3 looks at block timing. Data: a ~9 h mainnet
window (163,373 blocks, 8.753 % red), DAG and colouring from one node's RPC, and first-seen times on three of our
nodes (A, B, C), with peers pseudonymised. A *missed tip* is a block that one of our nodes had already seen before the
new block's header timestamp but that the new block does not reference. All results are associations: slow miners,
far-away miners and stale templates overlap, and none of this is a causal estimate.

Propagation (first-seen minus header timestamp, ms, p50 / p90): node A 386 / 784, node B 642 / 1,052, node C 397 / 816;
the spread between the three nodes has a median of 199 ms.

| Missed tips at the header timestamp | 0 | 1 | 2 | 3–4 | 5+ |
|---|---:|---:|---:|---:|---:|
| Red % | 3.87 | 13.43 | 30.27 | 50.40 | 68.38 |

| Earliest arrival minus header timestamp | < 200 ms | 200–400 ms | 400–600 ms | 0.6–1 s | 1–2 s | ≥ 2 s |
|---|---:|---:|---:|---:|---:|---:|
| Red % | 1.47 | 2.37 | 11.60 | 14.95 | 40.10 | 61.62 |

| Minutes since a pruning-point move | 0–2 | 2–5 | 5–10 | 10–15 | 15–30 | 30–60 | ≥ 60 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Red % | 44.14 (n = 256) | 19.68 | 17.40 | 15.47 | 8.54 | 7.17 | 8.01 |

- Blocks that missed no tip, by either their header timestamp or their arrival, were 64.4 % of blocks outside the
  post-move windows and were red 1.86 % of the time; the rest were red 18.92 % of the time.
- The 15 minutes after each pruning-point move hold 8.5 % of blocks but 17.2 % of all reds. During a move nodes
  process no blocks and serve no templates ([HTN-39](../findings/HTN-39.md), [HTN-40](../findings/HTN-40.md)).
- Parent count itself is not associated with red share up to 4 parents (8.08–9.14 %).

## Bridge template cache before and after (pre-registered)

R3 found that a solo miner behind our bridge often built on templates that missed a tip its node already knew, and that
93 % of those tips were younger than the bridge's 190 ms template-cache TTL. The bridge had stopped clearing that
cache on a new-block notification ([HTN-44](../findings/HTN-44.md)). The fix was deployed on that bridge and evaluated
against criteria locked before the data were analysed: (a) the missed-tip share must fall significantly; (b) a claim of
fewer red blocks requires the 95 % interval of the difference-in-differences (own change minus other miners' change)
to exclude zero. Windows: about 9 h before and 6 h after, each without the 15 minutes after a pruning-point move.

![Two panels. Left: share of own blocks missing a known tip, before 46.7 %, after 8.5 %; with a tip at least 50 ms old, before 32.2 %, after 0.18 %. Right: red share, own 2.07 % to 0.95 %, other miners 8.05 % to 6.78 %; not significant under the pre-registered difference-in-differences.](../figures/gbt-cache-before-after.svg)

- (a) met: 46.7 % → 8.5 % (z = −31.5); tips at least 50 ms old 32.2 % → 0.18 %. What remains is ordinary propagation.
- (b) not met: own red share 2.07 % → 0.95 %, other miners 8.05 % → 6.78 %; difference-in-differences +0.15 pp, 95 % CI
  [−0.61, +0.91]. The PR therefore claims fresher jobs, not fewer red blocks.
- Exploratory, not pre-registered: the relative-risk ratio (own 0.46 / others 0.84) is 0.54 [0.31, 0.95]. It suggests
  an effect but needs a new pre-registered window with this metric.

## Reproduction

The replay is a single-file Go program with four unit tests (ancestry against an independent transitive closure,
work and tie-breaking, cutoff boundaries, candidate-check semantics) and a summariser script. Inputs are the recorded
block headers, parents, difficulty bits and node colours. Runs: validate-only; full window; `-limit 90000 -strict-limit`;
`-strict-limit` on the full window (expected failure at block 92,335 for K=3). The programs will be published with the
upstream issue once the block export is reviewed for anonymisation. R3 and the template-cache comparison use a
feature extractor and a difference-in-differences script (Wilson intervals) over the same kind of export plus
per-node first-seen logs; they are published on the same terms.
