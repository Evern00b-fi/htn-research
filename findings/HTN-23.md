# HTN-23 — Wallet and mempool accept ML-DSA destinations before activation

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Medium | tooling | Code-confirmed | none | PR | Draft — not yet submitted | TBD |

## Summary

Consensus accepts ML-DSA P2PKH outputs today, the mempool treats them as standard, and `htnwallet` refuses to
*issue* but not to *send to* such addresses. Coins sent there are locked until an unscheduled fork.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `domain/miningmanager/mempool/check_transaction_standard.go:107`
- `domain/consensus/utils/txscript/standard.go:304`; `cmd/htnwallet/...` (no destination guard)

## Impact

Severity reasoning: likelihood is low (ML-DSA addresses are not issued by the wallet, so a user must obtain one from
elsewhere), but the consequence is indefinite loss of spendability, which exceeds "limited-impact correctness"; hence
Medium. An ML-DSA P2PKH address is a valid Bech32 address
(version 0x04), so a wallet or exchange that validates addresses generically will accept it as a destination; the
output is standard for the mempool and valid for consensus, but nothing can spend it until the gate activates, and no
activation is scheduled. P2SH forms are invisible to the mempool, so that part of the guard can only live in the wallet.

## Evidence

Static read of `standard.go:304`, `check_transaction_standard.go:107` and `create_unsigned_transaction.go` (no
guard), plus the passing wallet test that funds an ML-DSA coinbase output with the mainnet configuration.

## Recommendation

Wallet refuses ML-DSA destinations while `MLDSA44SignaturesActive(virtual)` is false; mempool treats such outputs as
non-standard until active. Policy only.

## Verification

**Completed:** static read and the passing wallet test that funds an ML-DSA output.

**Required before submission:** a mempool test (ML-DSA output before activation accepted before the change, rejected after) and a wallet destination test.

## Chain impact

None (mempool/wallet policy).

## Related items

[HTN-18](HTN-18.md)

## Upstream

TBD — PR/issue link to be filled in once submitted.

