# Public testnet on 2026-10-12 — facts

Related finding: [HTN-13](../findings/HTN-13.md). Snapshot date: 2026-10-12. Sources: the public network dashboard's
testnet statistics endpoint and the HTND source at tag `v2.17.4` and at `a56566e86`.

## Observed network

| Item | Value |
|---|---|
| Network | `hoosat-testnet` |
| Nodes reported | 2 |
| Peers seen by the reporting node | 1 |
| Reported server version | `2.17.4-a7eca4c79` |
| Block count / DAA score | 166,257 / 5,233,080 |
| Block rate | 5 BPS (300 blocks per 60 s) |
| Network hashrate | ≈ 50 kH/s |
| Difficulty | ≈ 5,002 |
| Estimated K | 1 (observed range 1–9) |
| Synced | yes |

Commit `a7eca4c79` was not an object in the public HTND repository on the snapshot date.

## Testnet rules in released code

| Source | Testnet `POWScores` entries | Highest block version | `HardForkGates` |
|---|---|---|---|
| tag `v2.17.4` | 8 | 9 | none |
| `a56566e86` (branch v2.18.1) | 12 (11 finite thresholds plus an unscheduled sentinel) | 12 at DAA score 1,534,673 | `testnetHardForkGates` at versions 10 and 12 |

The testnet's current DAA score (5,233,080) is far past the version-12 threshold in `a56566e86`. The unknown build
suffix `a7eca4c79` prevents equating the running network's rules with tag `v2.17.4`; establishing compatibility
requires the running build's source or a controlled joining test with a 2.18.x node. Neither was available on the snapshot date.

The ML-DSA-44 gate is block version 15 on every shipped network (mainnet, testnet, the B5/B10 test networks, simnet
and devnet); none of them reaches it.

## What this snapshot does not establish

- It does not establish that mainnet versions 10 and 11 were never exercised on a shared testnet before activation;
  the relevant builds and test records are requested from maintainers.
- It does not establish which build the testnet operator intends as canonical, nor which rules the running build applies.
- It does not demonstrate a shared network exercising current release parameters.
- It says nothing about the correctness of the testnet chain itself.
