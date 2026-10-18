# HTN-41 — `ConnectionManager.Stop` can block forever on waking a connection loop that has already returned

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Medium | availability | Reproduced | none | PR | Merged 2026-10-12 into 2.18.2 (5b1c9e3b6) — released in v2.18.2 (16 October 2026) | PR [HTND#36](https://github.com/HoosatNetwork/HTND/pull/36) |

## Summary

`ConnectionManager.Stop` sets the stop flag, disconnects peers, stops the ticker and then wakes the connection loop
with a send on the unbuffered `resetLoopChan`. The send completes only if the loop is parked in
`waitTillNextIteration`. If the loop's 30 s ticker fires between the flag and the send, the loop sees the flag and
returns, and `Stop` blocks forever; the node's shutdown then hangs until the outer timeout (HTN-05). If the loop is
mid-iteration (DNS seeding, dials), `Stop` waits for that iteration. A late wake-up from `AddConnectionRequest` after
the loop has returned leaks its goroutine.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `infrastructure/network/connmanager/connmanager.go:60` (unbuffered channel), `:88-101` (`Stop`), `:112, 180` (loop)

## Impact

A rare shutdown hang ending in the unclean exit of HTN-05. The window is short, so it is not the explanation of the
observed incident; it was found because a shutdown test hung unless it first waited for the loop to park.

## Evidence

`TestStopReturnsWhenTheConnectionLoopIsNotWaiting` uses the real `New` and `Stop` with no connection loop receiving,
so it tests the channel contract (a wake-up must not block when nobody is waiting, as for a loop that has returned or
is busy), not an actual running-loop shutdown schedule. It also sends a second wake-up into the full buffer. It fails on v2.18.1 head `fcef4aede` ("Stop blocked
on a connection loop that was not waiting for its wake-up", 5 s timeout) and passes with the change.

## Recommendation

Give `resetLoopChan` a buffer of one and make `run()` send without blocking (`select` with `default`). One pending
wake-up is enough, because an iteration handles everything pending; a loop that was busy during `Stop` finds the
buffered wake-up at its next wait and returns. About ten lines plus the test. `Stop` still does not wait for the loop
to return or cancel an in-flight dial, as today; this change only removes the blocking send.

## Verification

**Completed:** the test above fails on base and passes on the branch, `-race -count=20` (reproduced by the review); connmanager and integration
tests pass; merges cleanly with the HTN-05 and HTN-06 branches and master `c097146c6`, and the combination passes
`-race -count=5`.

**Required before submission:** none beyond review; with this change the HTN-05 test no longer needs its "loop parked"
barrier, which can be simplified in whichever PR lands second.

## Chain impact

None (node-local). Previously several blocked senders could each cause a redundant iteration; concurrent wake-ups
during one iteration are now coalesced into one further iteration.

## Related items

[HTN-05](HTN-05.md), [HTN-06](HTN-06.md)

## Upstream

PR [HTND#36](https://github.com/HoosatNetwork/HTND/pull/36) — merged, released in v2.18.2.

_AI disclosure: prepared with AI assistance (Claude by Anthropic; cross-reviewed with OpenAI Codex)._
