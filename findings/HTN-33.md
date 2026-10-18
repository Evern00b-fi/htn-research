# HTN-33 — Supply integrity: publish the emission model and a reproducible supply audit

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Informational | tooling | Documentation/tooling proposal; reconciliation unverified | none | Issue | Draft — not yet submitted | TBD |

## Summary

A public dashboard compares the UTXO-set total with a theoretical emission schedule and shows a difference that
its adjustments do not fully close. The figures shown there lack a cited consensus snapshot, a stated denominator and
an accounting definition sufficient to validate the percentages or the adjustments, so this repository draws no
conclusion from them. Dashboard discrepancies alone do not establish unauthorised issuance; they do show that the
community has no reproducible way to check supply.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `domain/consensus/processes/coinbasemanager/coinbasemanager.go` (subsidy schedule, merge-set rewards including red
  blocks since block version 10, dev fee)
- RPC: no supply-audit endpoint at a56566e86

## Impact

Without a published emission formula and an audit procedure, nobody outside the maintainers can reconcile scheduled
issuance with the UTXO set, and any dashboard figure becomes a source of speculation rather than information.

## Evidence

Documentation/tooling proposal; reconciliation unverified. The only inputs are public dashboard figures without a
documented methodology; no node-side computation was performed for this item.

## Recommendation

Publish a reproducible reconciliation of scheduled issuance, actual coinbase rewards, burns and the UTXO total at a
specified consensus state. Concretely: (a) document the exact emission formula the node implements, including red-block
rewards and the dev fee; (b) ship a small tool or RPC that, given a pruning point or DAA score, reports scheduled
issuance, paid rewards and the UTXO total from the node's own data. No supply intervention is proposed.

## Verification

**Completed:** none (proposal).

**Required before submission:** the tool reproduces the dashboard total from a node's UTXO set and the published formula
at one agreed consensus state.

## Chain impact

None (tooling/documentation). No supply intervention is proposed.

## Related items

none

## Upstream

TBD — PR/issue link to be filled in once submitted.

