# The first study (October 2026, HTND v2.18.1)

The study that started this work: a structured review of HTND v2.18.1 and its Kaspa parents, with measurements on our
own nodes. The general method that grew out of it, and that every item follows today, is in
[METHODOLOGY.md](../METHODOLOGY.md).

## 1. Question and plan

Operator experience motivated the work: nodes had failed roughly weekly with panics or an unusable database, and the
only fix had been a reset and a fresh IBD. The plan asked six questions: what the project's technical goals are and
whether the code meets them; which mechanisms reduce fault tolerance; whether the promised GHOSTDAG/DAGKnight benefits
hold at the current parameters; where HTND is stronger or weaker than its Kaspa parent; what the state of
post-quantum protection is; and which fixes should be proposed now, later, or only after a test.

The plan was written down first, reviewed by a second model, and revised before analysis started. The revision added
an explicit fault taxonomy (physical corruption · lost recent writes · inconsistent consensus/UTXO state · startup
refusal · resource exhaustion), a recovery oracle (reopened state must equal a deterministic replay or be refused
explicitly), file-system-level fault injection instead of plain `SIGKILL`, and a rule that every PR proposal needs a
failing reproducer, an acceptance test, a compatibility assessment and a rollback plan.

All code was pinned: HTND `a56566e86` (branch v2.18.1), HTND master `c097146c6`, kaspad `88bd604397`, rusty-kaspa
`01b532e8b5`, htn-stratum-bridge `3b2cf8c` (v1.8.0). Tests ran offline with a local Go 1.27.2 toolchain in scratch
worktrees; the pinned checkouts were never modified. No GitHub actions, installs or network access were used by the
analysis agents.

## 2. The six streams

| Stream | Topic | Acceptance criterion |
|---|---|---|
| S1 | Storage and recovery: Pebble options, destructive recovery, sync/WAL, LevelDB, staging atomicity, fault injection | For every injected fault: evidence preserved and recovery consistent, or an explicit refusal |
| S2 | Consensus state and IBD: interrupted pruning, UTXO sets, consensus switch, IBD and peer policy, repeated IBD | Interrupted execution equals uninterrupted replay |
| S3 | Lifecycle and resources: panics, shutdown (including upstream PR #25), unbounded queues, relay hot path | Every claimed race or leak reproduced |
| S4 | DAG quality and security: dynamic K, DAGKnight, red-block share, metric definitions, public data | Claims rest on defined metrics |
| S5 | PoW and post-quantum: block versions and activation, ML-DSA-44, test coverage, README claims | Activation and threat matrix plus tests |
| S6 | Project goals and Kaspa comparison: documents, claim/evidence matrix, inherited vs HTND-specific code | Comparison under equal criteria |

Each stream produced a report in a common format: scope and what was examined, a findings table (claim, failure
class, evidence, severity, confidence, upstream status, minimal fix, before/after test, category, compatibility and
rollback), a "looks bad but is fine" section to avoid false alarms, and open questions for maintainers or live data.
Measurement tasks ran alongside: R1/R2 on red blocks and R3 on block timing ([red-blocks.md](red-blocks.md)), a two-node
memory test ([memory-test.md](memory-test.md)), pruning-point move timings from three nodes (HTN-39, HTN-40), one full IBD
([ibd-timing.md](ibd-timing.md)), and a pre-registered before/after comparison of a bridge fix (HTN-44). Criteria for the
memory test and the bridge comparison were written down before the data were analysed.

## 3. Review process

1. **Synthesis.** The six stream reports were merged into one internal synthesis and a decision-ready backlog
   (one independent decision per item, each with a chain-impact line).
2. **First independent review (Claude).** Re-read the code at the pinned commit and re-ran the reproducers in its own
   worktree. Verified every actioned finding, issued line-level corrections, listed what the synthesis had missed, and
   answered two strategic questions (whether a better-established hardening exists for the PoW-hash field; which
   well-known measures are absent in HTND).
3. **Second independent review (Codex).** Reviewed the synthesis, the backlog and the first review with a mandate to
   disagree. It independently re-ran the key reproducers (arm64 PoW rejections 101/183 vs 0/183 on amd64; the pruning
   recovery failure on both test networks; rank = parent count on 1,806 parent sets; the R2 baseline, full-window and
   strict-prefix results), refuted or weakened several claims (section 4) and required that fix validation be recorded
   separately from finding evidence.
4. **Owner pass.** Applied the corrections, restored anonymised own measurements that the second review had
   over-redacted, and fixed the publication rules ([METHODOLOGY.md, section 5](../METHODOLOGY.md#5-publication-rules-for-measurements)).
5. **Adversarial review of four draft PRs (Codex).** Re-ran the supplied tests on base and branch, wrote new
   regressions and fault injections, and listed required changes (HTN-03, HTN-39, HTN-41, HTN-43). Its corrections are
   in section 4 and in each finding's *Status* and *Verification*.

Evidence levels in the findings describe the **evidence for the finding**, not the readiness of a fix. Fix validation
is stated separately in each finding's *Verification* section; for HTN-03 and HTN-43 the *Status* also records
the outcome of the adversarial PR review (HTN-39 was reworked after that review and later merged).

## 4. What was refuted or corrected

Listed honestly, because a review that reports only confirmations is not useful.

| Original claim | Outcome | Correction |
|---|---|---|
| A process crash loses at most the newest 32 KiB of WAL records | **Refuted** | Pebble queues multiple full WAL blocks asynchronously; a targeted test returned from `WriteRecord` with more than 256 KiB queued. No upper bound is established (HTN-27). |
| The internal shutdown budget is about 210 s | **Refuted** | The outer timeout is 120 s and *includes* the 90 s event drain. `component_manager.go` also returns after a drain timeout, so the database can be closed under a live handler even without the outer timeout (HTN-05, HTN-35). |
| The miner-supplied `PoWHash` field is stored in the database | **Refuted** | Serialisation omits it; the block-cache regression test confirms its loss after eviction (HTN-15). |
| "Most red blocks are caused by K, not topology" (R2) | **Refuted as an inference** | The experiment cannot separate the causal shares of the K rule, topology and delay; it shows a reduction at fixed topology only ([red-blocks.md](red-blocks.md)). |
| The current attack threshold is about 47.6–48.9 % | **Weakened** | `b/(1+b)` is a simplified-model figure; the live network's attack threshold was not measured. |
| CI runs no tests | **Weakened** | Per-push CI runs four named tests and one race package; a nightly race workflow runs the full suite; its results were not inspected by this review (HTN-19). |
| Relay difficulty recomputation costs about 15 % CPU | **Weakened** | 15 % of sampled CPU on an idle node, about 4 % of one core (HTN-09). |
| v10/v11 rules were never exercised on a shared testnet | **Weakened** | The snapshot cannot establish historical absence; the issue now asks for builds and records (HTN-13). |
| Most coins sit in P2PK addresses | **Weakened** | The wallet default is P2PK; the distribution of coins by address type was not measured (HTN-30). |
| The systemd restart lock causes the datadir wipe | **Refuted** | Lock contention and all tested transient errors refuse or fail without deleting (HTN-03). |
| kaspad has stability fixes after the fork point that HTND lacks | **Refuted** | Post-fork kaspad commits touch wallet, proto and README only. |
| HTN-03 draft wording: "replace an older quarantine" | **Corrected** | Never delete an existing quarantine; preserve both and stop (HTN-03). |
| HTN-06 draft wording: "disconnect under the lock" | **Corrected** | Snapshot under the lock, disconnect outside it (HTN-06). |
| Pruning reproducer is a production crash replay | **Caveated** | The fixture shrinks network parameters so that deletion happens (HTN-02). |
| Second review: shutdown socket reproducers | **Not independently reproduced** | Blocked by sandbox bind restrictions, not by a failure of the reproducers. The second review then wrote socket-free versions, which are now part of the HTN-06 tests. |
| HTN-03: quarantine the corrupted datadir | **Superseded** | An adversarial review found unbounded disk use, a half-deleting `RemoveAll` on a failing parent and no lock against a second opener; replaced by a bounded evidence bundle under a lifecycle lock, plus an in-place cut for older-WAL damage (HTN-43). |
| "Corruption after an OOM kill" | **Cause unknown** | Under NoSync an OOM kill can lose unflushed WAL data queued in user space (not only the newest 32 KiB), which pebble treats as a truncated tail of the newest WAL. The cause of our past incidents is unknown; HTN-02 is a plausible candidate only ([db-recovery.md](db-recovery.md)). |
| HTN-39 first draft: start the deferred update on the next block insertion | **Corrected** | Review showed the announcement could then wait behind the whole update; the update now normally runs after the announcement, and live readers of the pruning-point set finish it first. |
| HTN-39: the update always runs after the announcement; follow-ups cut the network stall to seconds | **Corrected** | Adversarial review: a best-effort early announcement only. Readers, trusted insertion, `ResolveVirtual` and a second pruning-point move (insertion 30) can run the update first; trusted insertion lost its post-update; no seconds-level promise is supported. Changes requested. |
| HTN-03 draft: lifecycle lock and evidence bundle make recovery safe | **Corrected** | Adversarial review: a failed lock allowed unlocked recovery, a fresh nested path regressed, a failed rename fell back to deletion in place, and the bundle is best-effort diagnostics (not fsynced), not a protected copy. v2.18.1 already deletes on corruption. Rework required. |
| HTN-43 draft: each repair step is crash-safe; 244 + 120 keys | **Corrected** | Adversarial review: one transient read error reduces 364 to 243 kept keys; later-WAL removals lack a durability barrier; the repair depends on the HTN-02 fix. The fixture keeps 243 + 121 = 364 keys. Prototype, not ready. |
| Older-WAL loss is bounded (8 × 64 MiB, minutes behind, no headers-proof IBD needed) | **Corrected** | Memtable options are configurable, large batches exist, and an offline node may restart behind its peers' pruning point. |
| MANIFEST damage is always silent | **Corrected** | An invalid record is truncated without an error, but a malformed marker name is reported as corruption. |
| Bridge template-cache fix reduces red blocks (HTN-44) | **Not supported** | The pre-registered difference-in-differences includes zero; only the mechanism (stale templates) is claimed. |

## 5. Limitations of this study

- Three nodes for timing analyses; the memory test has n = 2 and a confounded utxoindex/node factor.
- No real power-loss test; power loss was simulated with Pebble's crashable in-memory file system.
- No linux/arm64 or `GOAMD64=v3` execution; those platforms are inferred from compiler rules and disassembly.
- The network was near idle throughout; nothing here measures a loaded network or a first sync.
- R1/R2 use one node's historical view of the DAG; they observe neither propagation nor miner intent.
- The pruning reproducer uses shrunk network parameters.
- Five pruning-import tests fail at the pinned commit for reasons not yet classified (fixture or defect).
