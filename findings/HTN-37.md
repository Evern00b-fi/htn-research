# HTN-37 — Docs: describe the PoW-hash check as implemented

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Informational | docs | Code-confirmed | none | PR | Draft — not yet submitted | TBD |

## Summary

The README describes a "quantum-resistant PoW ... against Grover". The check compares a miner-supplied hash with
the node's own recomputation; it does not change the nonce search. Grover's quadratic speedup on nonce search is absorbed
by difficulty retargeting like any hashrate increase.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `README.md:12, 19`; `domain/consensus/utils/pow/pow.go:205-217`

## Impact

An unsubstantiated security claim in project documentation. A miner who finds a valid nonce by any search, Grover
included, obtains the matching hash for free, so an equality check cannot add work to the search. The real quantum
exposure for the chain is Shor's algorithm against the signature scheme, which is what the ML-DSA work (HTN-18) and
the address default (HTN-30) address.

## Evidence

Code read: `pow.go:205-217` compares the supplied string with the recomputed hash and returns invalid on mismatch or
absence; the nonce search and the target comparison are unchanged by the field.

## Recommendation

Factual wording: the field is a consistency check between the miner's and the node's PoW implementations and a
diagnostic for pools; it is not a defence against quantum search. Whether the field should remain required at all is
a separate design question (HTN-15); this item changes documentation only.

## Verification

**Completed:** code read.

**Required before submission:** none (documentation change).

## Chain impact

None.

## Related items

[HTN-15](HTN-15.md)

## Upstream

TBD — PR/issue link to be filled in once submitted.

