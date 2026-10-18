# HTN-11 — A failed pruning-point UTXO update must not livelock the node

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Medium | availability | Code-confirmed | none | Issue | Draft — not yet submitted | TBD |

## Summary

While the update flag is set, every block insertion and every resolve chunk reruns the multi-minute pruning-point
UTXO update under the consensus lock, and an already-committed block is reported invalid. The mandatory commitment check
(commit `0f93c682b`; optional in kaspad) halts on a real mismatch.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `domain/consensus/processes/blockprocessor/validate_and_insert_block.go:191`
- `domain/consensus/consensus.go:1644`
- `domain/consensus/factory.go:674, 738`

## Impact

Possible consequence, not reproduced end to end: "stop on inconsistency" becomes a livelock in which the node stays
up, holds the lock for minutes per block and never recovers. Triggers include HTN-02 and any not-found during diff derivation.

Since [HTND#77](https://github.com/HoosatNetwork/HTND/pull/77) (merged into 2.18.3) a commitment mismatch found at
runtime stops the node cleanly with a short diagnostic instead of re-running the update on every block; the
livelock remains possible for other failures of the update itself.

## Evidence

Code paths above; not observed in the logs available to us.

## Recommendation

Options: (a) do nothing; (b) latch the failure once per start, surface an explicit fatal state naming the pruning
point, method and hashes, and add a startup check that refuses to run with an inconsistent pruning-point UTXO set and
prints "resync required". Recommendation: (b). Decision requested: is halt-on-mismatch permanent, and is (b) acceptable?

## Verification

**Completed:** code read.

**Required before submission:** a test that corrupts one UTXO bucket entry and asserts that the next N block insertions do not rerun the update.

## Chain impact

None (node-local).

## Related items

[HTN-02](HTN-02.md)

## Upstream

TBD — PR/issue link to be filled in once submitted.

