# HTN-30 — Default wallet address type is P2PK, exposing public keys at rest

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Low | tooling | Code-confirmed | none | Issue | Draft — not yet submitted | TBD |

## Summary

`htnwallet` defaults new receive addresses to P2PK (the public key is in the address); P2PKH hides the key until
spend. The distribution of coins by address type was not measured, so this is a statement about the default, not
about how many coins are affected today.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `cmd/htnwallet/daemon/server/address.go:335-336`; `util/address.go:22`

## Impact

Keys of unspent outputs are exposed on chain earlier than necessary; this matters for any future migration to
post-quantum signatures.

## Evidence

`address.go:335-336` selects P2PK; `util/address.go:22` defines its address version. The ML-DSA address type already
uses a hash (version 0x04), so the wallet has the hashing pattern available.

## Recommendation

Options: retain P2PK defaults, or default new receive addresses to P2PKH after compatibility tests. Recommendation:
P2PKH for fresh, unexposed keys; existing addresses are unaffected and keep working. Decision requested: approve the
default change and its rollout (wallet release note, no node change)?

## Verification

**Completed:** code read.

**Required before submission:** wallet tests for the new default; send/receive compatibility across wallet versions and with the bridge's payout address validation.

## Chain impact

None (wallet only).

## Related items

[HTN-18](HTN-18.md)

## Upstream

TBD — PR/issue link to be filled in once submitted.

