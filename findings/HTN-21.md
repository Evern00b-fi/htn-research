# HTN-21 — Hard-fork gate tests pin stale constants; one would activate ML-DSA if "fixed" naively

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Low | tooling | Reproduced | none | PR | Draft — not yet submitted | TBD |

## Summary

Four tests fail at a56566e86 because gates were scheduled on purpose: `TestMLDSA44IsInertOnEveryNetwork`
(expects 11, gate is 15), `TestStrictCoinbaseGateIsUnscheduled`, `TestGatedChecksAreUnscheduledOnMainnet`,
`TestUnscheduledHardForkGatesAreInertOnEveryNetwork`. Restoring gate 11 to make the first test pass would activate
ML-DSA on mainnet at the v11 fork.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `domain/consensus/processes/transactionvalidator/*_test.go`, `blockvalidator/*_test.go`, `consensusstatemanager/*_test.go`, `domain/consensus/*_test.go`
- `domain/dagconfig/params.go:333, 339`

## Impact

Lost regression coverage on the guard that the 2.18.0 notes describe as "rejects production writes to any hard-fork
gate", plus an unsafe "fix" path: a contributor who makes `TestMLDSA44IsInertOnEveryNetwork` pass by restoring the
constant 11 would schedule ML-DSA on mainnet at the version-11 fork. The test also skips the B5/B10 networks and is
not run in CI (HTN-19), so the failures were not visible to maintainers.

## Evidence

All four fail when run (`go test -run 'TestMLDSA44IsInertOnEveryNetwork|TestStrictCoinbaseGateIsUnscheduled|TestGatedChecksAreUnscheduledOnMainnet|TestUnscheduledHardForkGatesAreInertOnEveryNetwork' ./domain/...`);
confirmed by the second reviewer.

## Recommendation

Assert the property "ML-DSA inactive at the highest finite `POWScores` version on every network" instead of a
constant; pin the other gates to their scheduled values. Test-only.

## Verification

**Completed:** all four tests fail at a56566e86; confirmed by the second reviewer.

**Required before submission:** the rewritten tests pass now and fail if a gate is set at or below a reachable version.

## Chain impact

None (tests only).

## Related items

[HTN-18](HTN-18.md), [HTN-19](HTN-19.md)

## Upstream

TBD — PR/issue link to be filled in once submitted.

