# HTN-40 — The pruning-point UTXO commitment scan holds the consensus lock for minutes on every move

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Medium | availability | Measured | none | Issue | Merged 2026-10-18 into 2.18.3 (a94e94058) as PR #77, the approach chosen in #41 | Issue [HTND#41](https://github.com/HoosatNetwork/HTND/issues/41), PR [HTND#77](https://github.com/HoosatNetwork/HTND/pull/77); follow-up [HTND#42](https://github.com/HoosatNetwork/HTND/issues/42) |

## Summary

`updatePruningPoint` checks that the UTXO set it is about to serve matches the new pruning point's header commitment
(`validateUTXOSetFitsCommitment`). The check is worthwhile: a node must not hand IBD peers a set that does not match.
It was added to this path in October 2026. It hashes the whole set, about 20.7 M entries on mainnet in our node logs, while the
consensus lock is held, so on every move the node builds no templates, validates no transactions and processes no
blocks for 2–4 minutes.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `domain/consensus/consensus.go:1644` (update inside the virtual update, under the consensus lock)
- `domain/consensus/processes/pruningmanager/pruningmanager.go:2585` (call), `:1218` (full scan)
- Waiting on the same lock: `BuildBlockTemplate`, `ValidateTransactionAndPopulateWithConsensusData`, `GetVirtualInfo`, `GetVirtualDAAScore`

## Impact

Pools and bridges get no new templates and wallets cannot submit transactions during the move. Red blocks
concentrate after moves: in a 9-hour, 163k-block analysis the 15 minutes after each move held 8.5 % of blocks but
17.2 % of red blocks, and blocks in the first 2 minutes were 44 % red. Combined with HTN-39 the network-wide pause
reaches about 6 minutes.

## Evidence

Our own log measurements, one move, three of our nodes on 2.18.1:

| Node | Total update | Restore from acceptance data | Commitment scan | Deletion + commit |
|---|---|---|---|---|
| C (8 vCPU) | 2 min 5 s | 5 s | 1 min 57 s (94 %) | 1.6 s |
| A (6 vCPU) | 4 min 3 s | 25 s | ~3 min 35 s (88 %) | not logged separately |
| B (6 vCPU) | 3 min 27 s | 45 s | 2 min 40 s (78 %) | not logged separately |

Under a 7 GiB memory cap the same nodes took 6 min 20 s (A) and 5 min 17 s (B) for a later move, and an RPC call
timed out after 30 s waiting for the lock ([reports/memory-test.md](../reports/memory-test.md)).

## Recommendation

Issue for design input, two node-local options that keep the check's guarantee. **A:** under the lock write the diff
and commit (restore alone took 5–45 s above; not measured for option A); run the full
scan in the background on a pebble snapshot; delete past blocks and clear the flag in one commit (HTN-02) only after
it passes; refuse to serve the new set until then. **B:** verify incrementally (previous verified multiset ± this
move's diff, O(diff)) and keep A's scan as a slower background check. A follow-up
issue proposes moving the whole update into a dedicated background task.

## Verification

**Completed:** phase timings from three nodes; lock holders identified in code.

**Required before submission:** maintainer answers (should a mismatch halt the node or only stop serving; scan every
move or only for some diff methods); then a PR with a negative test (a corrupted bucket is not served, nothing deleted,
flag kept) and a positive test (blocks keep flowing during the scan).

## Chain impact

None (node-local).

## Related items

[HTN-39](HTN-39.md), [HTN-02](HTN-02.md), [HTN-17](HTN-17.md), [HTN-04](HTN-04.md)

## Upstream

Issue [HTND#41](https://github.com/HoosatNetwork/HTND/issues/41) and follow-up [HTND#42](https://github.com/HoosatNetwork/HTND/issues/42) — in review.

