# HTN-13 — Public testnet does not run the current release parameters

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Medium | process | Measured | none | Issue | Draft — not yet submitted | TBD |

## Summary

A public snapshot on 2026-10-12 shows a testnet of 2 nodes, build `2.17.4-a7eca4c79` (a commit not in the public
repository), ~50 kH/s and K mostly 1. Released code differs on testnet rules: tag v2.17.4 has 8 `POWScores` entries
(version 9 max) and no `HardForkGates`; a56566e86 has 12 entries (11 finite thresholds reaching version 12, plus an
unscheduled sentinel) and `testnetHardForkGates`. The unknown build suffix prevents equating the running network's
rules with tag v2.17.4; compatibility requires the running build's source or a controlled joining test. See
`reports/testnet-state.md`.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `domain/dagconfig/params.go` (testnet `POWScores`, `testnetHardForkGates`) at tag v2.17.4 vs a56566e86

## Impact

This snapshot does not demonstrate a shared network exercising current release parameters, which the K-floor study
(HTN-04), ML-DSA activation (HTN-18) and fork rehearsals (HTN-14) would need. It does not establish historical absence
of testnet coverage for v10/v11; the relevant builds and test records are requested.

## Evidence

Public testnet statistics snapshot (node count, build string, hashrate, K range); `params.go` comparison between
tag v2.17.4 and a56566e86.

## Recommendation

Options: (a) do nothing; (b) reset or realign the testnet to 2.18.x parameters and publish the build; (c) start a
fresh network from the existing `hoosat-testnet-b5` parameters. Recommendation: (b) or (c); community operators can
supply nodes, a miner and a faucet. Decision requested: which network and parameters are canonical for pre-activation
testing, and who publishes the binary?

## Verification

**Completed:** public snapshot and `params.go` comparison.

**Required before submission:** the running build's source, or a controlled joining test with a 2.18.x node; a block-version transition exercised there before mainnet.

## Chain impact

None for mainnet; a testnet reset affects only the test network.

## Related items

[HTN-14](HTN-14.md), [HTN-04](HTN-04.md), [HTN-18](HTN-18.md)

## Upstream

TBD — PR/issue link to be filled in once submitted.

