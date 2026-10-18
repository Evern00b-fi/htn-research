# HTN-39 — The block that moves the pruning point is relayed only after its UTXO update; stalls cascade hop by hop

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Medium | availability | Measured | none | PR | Merged 2026-10-13 into 2.18.2 (38a586e04) — released in v2.18.2 (16 October 2026) | PR [HTND#47](https://github.com/HoosatNetwork/HTND/pull/47) |

## Summary

When a block moves the pruning point, `ValidateAndInsertBlock` commits it and then runs the pruning-point UTXO set
update (2–4 minutes on mainnet, HTN-40) before returning. The relay flow announces a block only after that, so each node
holds the moving block for its whole update. Blocks built on it are orphans to nodes without it, so a node receives the
moving block only after a peer has finished its update, then starts its own: the stalls add up hop by hop.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `domain/consensus/processes/blockprocessor/validate_and_insert_block.go:191` (update inside insertion)
- `app/protocol/flows/v8/blockrelay/handle_relay_invs.go:371, 425` (`processBlock`, then `relayBlock`)
- Selection is deterministic: `nextPruningPointAndCandidateByBlockHash`

## Impact

About seven times a day the network stops processing blocks for several minutes, longer than any single node's
update. In the move below, node A processed no blocks for about 6 minutes although its own update took 4 minutes.

## Evidence

Our own log measurements: three of our nodes on 2.18.1 (A and B: 6 vCPU; C: 8 vCPU), same parameters, same pruning
point, identical blue scores. Start of each node's update, relative to the first node, for five consecutive moves:

| Move | C | A | B |
|---|---|---|---|
| 1st | +0.0 s | +0.6 s | +0.2 s |
| 2nd | +0.0 s | +38.3 s | +67.8 s |
| 3rd | +0.0 s | +102.4 s | +46.6 s |
| 4th | +0.0 s | +50.7 s | +50.9 s |
| 5th | +0.0 s | +107.9 s | +108.1 s |

In the 5th move A and B were at the tip, processed nothing from 4 s before t = 0, received the moving block within
0.12 s of each other at +108 s from a peer that had finished its update, and then updated for 243 s (A) and 207 s (B).

![Timeline of the 5th move: C updates from 0 to 125 s; A and B wait without processing blocks until about 108 s, then update until 351 s (A) and 315 s (B). Lower panel: update phases per node, and the same nodes under a 7 GiB memory cap, where the update takes 380 s (A) and 317 s (B).](../figures/pp-move-cascade.svg)

## Recommendation

Draft PR, a best-effort early announcement: an opt-in option makes `ValidateAndInsertBlock` return with the update
pending; relay, `SubmitBlock` and IBD run it after announcing the block. Live readers of
the bucket finish it first. Exceptions where the update still runs before the
announcement: readers (IBD serving, acceptance-data iteration), trusted insertion, `ResolveVirtual`, and a second
pruning-point move (insertion 30 in the extended test). The review also requires restoring the update after trusted
insertion and an explicit error policy. This could shorten the network-wide stall; the update itself is not shorter.

## Verification

**Completed:** `TestPruningPointMoveReturnsBeforeItsUTXOSetUpdate` (both nets, six subtests) fails on base
`fcef4aede` and passes on the branch, also with `-race` (reproduced by the review; not a proof of announcement
ordering); without the reader guards it fails 4/6.

**Required before submission:** the review changes above; deterministic tests of a reader between commit and
announcement and of a second move; a before/after timing; maintainer view on strict ordering.

## Chain impact

None (node-local). No consensus rule, P2P message or database format change.

## Related items

[HTN-40](HTN-40.md), [HTN-02](HTN-02.md), [HTN-11](HTN-11.md), [HTN-04](HTN-04.md)

## Upstream

PR [HTND#47](https://github.com/HoosatNetwork/HTND/pull/47) — merged, released in v2.18.2.

_AI disclosure: prepared with AI assistance (Claude by Anthropic; cross-reviewed with OpenAI Codex)._
