# HTN-14 — Hard-fork lead time and a testnet-first policy

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Medium | process | Code-confirmed | none | Issue | Draft — not yet submitted | TBD |

## Summary

v10 was activated and reverted the same day (`252e0adc5` -> `6bf71257f`, 2026-09-19, "live outage"); v11 was
scheduled by a commit on 2026-10-06 with a documented target of 2026-10-12. The local review snapshot contained no
v2.18.1 tag; pre-activation release-note availability was not established.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- Commits `252e0adc5`, `6bf71257f`, `c37a0bc1e` (git history)
- `domain/dagconfig/params.go` `POWScores`

## Impact

Short release lead time limits upgrade preparation and public validation. The v10 episode shows the cost: the only
node running the new rules stalled and the activation had to be reverted the same day. The v11 schedule left six days
between the scheduling commit and the documented activation target.

## Evidence

Git history of the gate commits (dates verified); absence of a v2.18.1 tag in the local snapshot. The activation
date itself is the documented target, not independently verified activation evidence.

## Recommendation

Options: (a) do nothing; (b) policy: tagged release and notes at least N weeks before the activation DAA score,
exercised first on the HTN-13 testnet, plus an `IsUpgradeRequired` warning in logs and RPC as activation nears.
Recommendation: (b) with N = 2-4. Decision requested: adopt the policy and N?

## Verification

**Completed:** git history of the gate commits.

**Required before submission:** none (process item); verifiable later by the presence of a tag, notes and a testnet run before the next activation.

## Chain impact

None (process).

## Related items

[HTN-13](HTN-13.md), [HTN-28](HTN-28.md)

## Upstream

TBD — PR/issue link to be filled in once submitted.

