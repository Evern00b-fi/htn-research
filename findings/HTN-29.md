# HTN-29 — No storage mass (KIP-9 style) bounds UTXO-set growth

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Low | consensus | Code-confirmed | version-gated forward fork | Issue | Draft — not yet submitted | TBD |

## Summary

There is no storage mass anywhere in HTND (0 non-test hits); UTXO growth is bounded only by mempool policy, which
miners can bypass. rusty-kaspa applies KIP-9 storage and transient mass in consensus.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- Absence verified by grep over `domain/` at a56566e86

## Impact

Long-term disk and RAM growth outside node control; relevant to the 8 GB host goal (HTN-17). Compute mass constrains
per-block output creation; no storage-specific pricing bounds long-term growth, and node-local mempool rules
(compound-transaction rate limiter, frozen addresses) do not apply to transactions a miner includes directly.

## Evidence

Grep; live average is about 1.07 transactions per block, so the issue is prospective.

## Recommendation

Options: (a) do nothing; (b) adopt KIP-9-style storage mass at a fork. Recommendation: evaluate (b) with live
UTXO-growth data. Decision requested: is bounding UTXO-set growth a consensus goal?

## Verification

**Completed:** grep for storage mass (0 non-test hits).

**Required before submission:** design review plus testnet trial if (b) is chosen.

## Chain impact

(b) forward hard fork, version-gated.

## Related items

[HTN-17](HTN-17.md), [HTN-38](HTN-38.md)

## Upstream

TBD — PR/issue link to be filled in once submitted.

