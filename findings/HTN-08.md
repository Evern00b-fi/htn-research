# HTN-08 — Three unused GHOSTDAG caches preallocate about 343 MB per node

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Medium | memory | Reproduced | none | PR | Merged 2026-10-12 into 2.18.2 (1349729f8) — released in v2.18.2 (16 October 2026) | PR [HTND#39](https://github.com/HoosatNetwork/HTND/pull/39) |

## Summary

`ghostdagmanager.go` preallocates `chainPathCache` (2000), `lcaCache` (5000) and `agreesCache` (10000) per
manager; nothing reads or writes them since commit `78da7235d`, and there is one manager per block level (226).

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `domain/consensus/processes/ghostdagmanager/ghostdagmanager.go:57-59`
- Commit `78da7235d` (removed the last users)

## Impact

About a third of a gigabyte of resident heap on every node with no function. Relevant to the memory-budget question
(HTN-17).

## Evidence

- Heap profile of a production node at T+30 min after start (HTND 2.18.1-a56566e86, defaults): the three pools and maps
  account for **342.9 MB** of in-use heap.
- Arithmetic agrees: ~17,000 entries x 64-80 B plus map headroom, x 226 managers, about 340 MB.
- Deterministic Go test (second reviewer): heap after GHOSTDAG manager construction 353.6 MB before, 10.7 MB after
  removal (saving 342.9 MB); the targeted test subset passes before and after.
- DAGKnight code is a negligible CPU share, so the caches have no performance rationale.

## Recommendation

Delete the three fields and their initialisation; keep `umcVotingCache`. Target: master + v2.18.1.

## Verification

**Completed:** heap profile on our node; deterministic construction-heap test (353.6 MB before, 10.7 MB after).

**Required before submission:** the construction-heap test with a >= 300 MB threshold included in the PR; existing GHOSTDAG and DAGKnight tests pass.

## Chain impact

None (node-local).

## Related items

[HTN-17](HTN-17.md)

## Upstream

PR [HTND#39](https://github.com/HoosatNetwork/HTND/pull/39) — merged, released in v2.18.2.

_AI disclosure: prepared with AI assistance (Claude by Anthropic; cross-reviewed with OpenAI Codex)._
