# HTN-36 — Docs: describe GHOSTDAG K as implemented rather than as DAGKnight

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Informational | docs | Code-confirmed | none | PR | Draft — not yet submitted | TBD |

## Summary

The README says the node "utilizes the DAGKnight protocol". For block version >= 6, K equals the number of direct
parents (rank over an antichain = |parents|, verified on 1806 parent sets); chain selection remains GHOSTDAG by blue
work, and `OrderDAG` only orders pending tips locally. `dagknight-faithfulness.md` is an AI-generated assessment that
describes caches no longer present.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `README.md`; `domain/consensus/processes/ghostdagmanager/dagknight-faithfulness.md`

## Impact

Readers, including exchanges and researchers assessing the chain's security, assume a latency-adaptive protocol with
DAGKnight's properties, while the running protocol is GHOSTDAG with a per-block K equal to the miner's parent count and
a static K=40 for pruning depth. The AI-generated faithfulness document rates the rank computation highly although the
rank collapses to |parents|, and it describes an MD5-based cache that no longer exists.

## Evidence

`TestS4RankEqualsParentCount` (1806/1806); code read.

## Recommendation

Neutral wording ("K = parent count, capped at 12; GHOSTDAG chain selection"); mark `dagknight-faithfulness.md`
non-normative or remove it.

## Verification

**Completed:** `TestS4RankEqualsParentCount` (1806/1806); code read.

**Required before submission:** none (documentation change).

## Chain impact

None.

## Related items

[HTN-04](HTN-04.md)

## Upstream

TBD — PR/issue link to be filled in once submitted.

