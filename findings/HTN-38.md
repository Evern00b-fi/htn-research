# HTN-38 — Rationale for consensus parameters at 5 BPS is undocumented

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Informational | docs | Code-confirmed | none | Issue | Draft — not yet submitted | TBD |

## Summary

Coinbase maturity is 100 blocks = 20 s; merge depth 3600 blocks (12 min); finality 3 h; pruning about 7.6 h;
static K=40 versus 67 from Kaspa's formula at 5 BPS. These may be intentional, but no rationale is documented and no
whitepaper or specification was found.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `domain/dagconfig/params.go:84-86, 516-541`

## Impact

Reviewers and future maintainers cannot tell deliberate choices from inherited defaults. Several values look like
kaspad's 1 BPS constants carried over unchanged (100-block maturity, 2640-block windows) while others were changed
(finality, pruning depth), so the overall safety margin at 5 BPS is unclear. rusty-kaspa derives each of these from
BPS and a delay bound in one place (`bps.rs`), which makes the reasoning auditable.

## Evidence

Parameter values read at a56566e86; comparison with kaspad and rusty-kaspa derivations.

## Recommendation

Options: (a) do nothing; (b) document the rationale; (c) re-derive at a fork. Recommendation: (b) first.
Decision requested: provide or co-author the rationale?

## Verification

**Completed:** parameter values read; comparison with kaspad and rusty-kaspa.

**Required before submission:** none (documentation/issue).

## Chain impact

None (documentation).

## Related items

[HTN-04](HTN-04.md), [HTN-29](HTN-29.md)

## Upstream

TBD — PR/issue link to be filled in once submitted.

