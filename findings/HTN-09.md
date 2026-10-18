# HTN-09 — Block relay recomputes required difficulty twice per block through `GetVirtualInfo`

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Medium | performance | Measured | none | PR | Draft — not yet submitted | TBD |

## Summary

`handleRelayInvsFlow` calls `GetVirtualInfo()` twice per processed block. That call recomputes
`RequiredDifficulty` over the 2640-block window under the consensus lock, but the flow uses only `ParentHashes`.
Inherited from kaspad, where 1 BPS makes it five times rarer.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `app/protocol/flows/v8/blockrelay/handle_relay_invs.go:359, 399`
- `domain/consensus/consensus.go:1229-1268`, `difficultymanager.go:134-146`

## Impact

Wasted CPU and lock hold time on the hot path; it grows with block rate and peer count.

## Evidence

- 30 s CPU profile (pprof) of an idle mainnet node (6 vCPU / ~11 GiB KVM; HTND 2.18.1-a56566e86):
  `GetVirtualInfo -> RequiredDifficulty` is ~15 % of CPU samples (~4 % of one core), about half the cost of block
  validation itself. This is a share of samples on an idle node, not 15 % of a core.
- Synthetic bench `TestS3GetVirtualInfoCost` (linear 2700-block chain, headers cached): 199 us per `GetVirtualInfo`
  vs 175 ns per virtual-parents read. Production calls are slower (wider DAG, header-cache misses).

## Recommendation

Add `Consensus.GetVirtualParents()` (one `BlockRelation(virtual)` read under the lock) and use it at both sites.
No cache, so no invalidation risk. Target: master + v2.18.1.

## Verification

**Completed:** CPU profile and synthetic benchmark.

**Required before submission:** equivalence test: after every insert, `GetVirtualParents()` equals `GetVirtualInfo().ParentHashes`.

## Chain impact

None (node-local).

## Related items

none

## Upstream

TBD — PR/issue link to be filled in once submitted.

