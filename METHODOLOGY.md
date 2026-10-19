# Methodology

How we work, from a first observation to a tested fix and to the testing of every new HTND build. The same rules
apply to every item; the first study that started this work (October 2026, HTND v2.18.1) is described on its own in
[reports/first-study-2026-10.md](reports/first-study-2026-10.md), including the claims that were refuted there.

In short: every finding comes from pinned code and is checked by a second, independent reviewer. Every fix has a test
that fails before the change and passes after it. Larger changes are compared side by side, first on a private test
network and then on the public testnet. Every new HTND build runs on the public testnet and is re-tested.

## 1. From observation to finding

- **Starting points.** Operator experience (crashes, stalls, memory growth), our own measurements, and reading the
  code of HTND, the stratum bridge and their Kaspa parents.
- **Pinned code.** Every analysis names the exact commit it read. Tests run offline in scratch copies; the pinned
  checkout is never modified.
- **Reproduce or confirm.** A claim becomes a finding only when a test reproduces it at the pinned commit, or when the
  code and its history establish it. Measurements are labelled as measurements; anything else stays a hypothesis.
- **Independent second review.** A different model from the one that produced the finding re-reads the code and
  re-runs the reproducers, with a mandate to disagree. Refuted or weakened claims are recorded, not deleted.
- **Evidence levels.** Each finding says how strong its evidence is (defined in [FINDINGS.md](FINDINGS.md)):
  *Reproduced* means a test fails at the pinned commit (and passes with a fix where one exists), re-run at least
  twice; *Code-confirmed* means established by reading pinned code and history; *Measured* means observed in
  anonymised operational or public data; *Hypothesis* means plausible but the decisive observation is missing.
  Severity follows the impact on node operators and the chain, not the size of the fix. The evidence level describes
  the finding, not the readiness of a fix; fix validation is stated separately in each finding.

## 2. From finding to fix

- **Discussion first where needed.** A clear-cut fix goes straight to a pull request. A finding that needs a
  decision first (a design choice, a trade-off, or a change in behaviour) is opened as a public issue (or reported
  privately, see below) before any code is proposed, so that the Hoosat developers can decide the direction.
- **One finding per pull request.** Small, separate pull requests are easier to review and to revert.
- **Fail before, pass after.** Every pull request carries a test that fails on the base commit and passes with the
  change, plus a note on compatibility and on how to roll it back.
- **Adversarial review.** Larger pull requests are reviewed by a second model that re-runs the tests on base and
  branch and tries to break the change; its findings are fixed before submission.
- **Chain impact stated.** Every finding and pull request says whether it changes consensus, node-local behaviour
  only, or nothing on the chain.
- **Security-sensitive findings** are reported privately to the Hoosat developers and published only after the fix
  is released and disclosure is agreed.

## 3. Comparing builds

A change that may affect performance or consensus timing is compared "with" and "without" before conclusions are drawn.

- **Private test network.** A throw-away network of five nodes on a temporary cloud server, deleted afterwards:
  load, partitions, kill tests and A/B runs. Pass rules are written down before the run.
- **Known noise level.** The private network's noise was measured once by running the same build on both sides
  (an A/A run). An A/B difference smaller than that noise is not reported as an effect.
- **Side by side on the public testnet.** The new build and the previous build run on identical machines with the
  same settings, each synced from scratch from the public testnet. Neither side changes version during the run.
  Compared: the consensus results (the same pruning points, UTXO commitments and a sample of blocks), the time of
  each pruning-point move phase, memory, CPU and block gaps.
- **Light, identical profiling.** Comparison runs use the same light profiling on both sides. Full profiling slows
  the node and changes timings, so it is never used in a comparison run.
- **Every anomaly gets a cause.** A restart, a cold cache or a load spike is identified and shown apart before any
  figure is compared. Small samples are reported as ranges, not as single figures.

## 4. Testing of every new build

Since 17 October 2026, each new HTND build goes through these three steps automatically:

1. **Testnet acceptance.** One of our nodes on the public Hoosat testnet follows the maintainers' current branch and
   runs an acceptance pack on each new build: sync from scratch, block acceptance, memory and restart behaviour, with
   a small share of the testnet's mining so that the node also produces blocks.
2. **Private network experiments.** Larger changes are compared on the private test network of section 3.
3. **Regression suite.** The fail-before/pass-after tests from our pull requests are re-run on every new build to
   record which items are fixed upstream and which remain.

Results go to the Hoosat developers per build; summaries appear in [CHANGES.md](CHANGES.md) as releases ship.

## 5. Publication rules for measurements

Own measurements are included as evidence in anonymised, reproducible form: machine class (vCPU/RAM/disk/virtualisation),
HTND version and relevant flags, method, script or test name, relative times ("~0.1 s after", "T+30 min"), nodes as
A/B, aggregates (median/p95/max) and log excerpts stripped of addresses. Excluded: IP addresses, hostnames, domains,
provider or region, wall-clock times of our restarts, ports, wallet addresses, worker names, raw profiles, and figures
about third-party software (which are reported to that software's developers only).

## 6. Limitations

- Few nodes, one operator. Node letters A, B, C denote the same machines throughout the repository.
- The testnet is smaller than mainnet (its UTXO set is about a quarter of mainnet's), so testnet times are not
  mainnet times.
- The public testnet is usually lightly loaded; heavy load is normally tested only on the private network, and on
  the public testnet only when the Hoosat core team asks for it.
- Security-sensitive findings are excluded from this repository until their fix is released.
- The authors are node operators, not core developers; maintainers may know rationale that the code does not record.

## 7. AI-assistance statement

This report was prepared with AI assistance (Claude by Anthropic; cross-reviewed with OpenAI Codex). Tests were run as described.

The analysis streams, reproducers, measurements scripts, syntheses and reviews were drafted by AI models (Anthropic
Claude and OpenAI Codex) working in sandboxed, offline worktrees on pinned checkouts, and were cross-reviewed by a
different model from the one that produced them. A human operator set the questions, ran the live-node measurements,
reviewed every claim against the cited code and data, applied the corrections, and decides what is published or
submitted. Every statement in this repository is the human owner's responsibility. Every pull request, issue and private
advisory text carries the same disclosure: developed with Claude (Anthropic), cross-reviewed with OpenAI Codex, and
reviewed and tested by the submitter, who takes responsibility for it. Items are labelled with their
evidence level so that readers can weigh AI-derived reasoning accordingly.
