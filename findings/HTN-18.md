# HTN-18 — ML-DSA-44 activation readiness

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Medium | consensus | Code-confirmed | version-gated forward fork | Issue | Draft — not yet submitted | TBD |

## Summary

The ML-DSA-44 gate is block version 15; mainnet `POWScores` reach version 11, so the feature is inert on every
shipped network. Prerequisites for a safe activation are missing or unsequenced: HTN-21, HTN-23, FIPS 204 KAT/ACVP
vectors (absent), a review that every transaction-validation path derives its script flags from the same
activation rule, a testnet run (HTN-13) and lead time (HTN-14).
Script limits cap ML-DSA multisig at 2-of-11.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `domain/dagconfig/params.go:339, 392` (gate), `txscript/mldsa44_multisig.go:19-30`, `txscript/mldsa44_test.go`

## Impact

Without sequencing, an activation would ship with known latent divergences and untested vectors.

## Evidence

Probe `TestS5ProbeMLDSAReach`: highest reachable version per network is mainnet 11, testnet 12, simnet 2, devnet 5.
ML-DSA verify cost 33-93 us vs Schnorr 38 us (M2). The measured verification cost did not show disproportionate cost
in this benchmark; broader resource-exhaustion behaviour was not assessed.

## Recommendation

Options: (a) leave dormant; (b) sequence the prerequisites and set a target. Recommendation: (b) as one readiness
decision with separate implementation tasks. Decision requested: target version/DAA score and order.

## Verification

**Completed:** reachability probe; verification benchmark.

**Required before submission:** each prerequisite's own test; the activation boundary exercised on the testnet with a pruning/IBD replay; the validation-path flag review.

## Chain impact

Forward hard fork, version-gated at a future DAA score (the gate already exists at version 15).

## Related items

[HTN-21](HTN-21.md), [HTN-23](HTN-23.md), [HTN-13](HTN-13.md), [HTN-14](HTN-14.md)

## Upstream

TBD — PR/issue link to be filled in once submitted.

