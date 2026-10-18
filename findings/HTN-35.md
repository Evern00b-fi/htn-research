# HTN-35 — Docs: systemd unit in the node guide lacks `TimeoutStopSec`

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Informational | docs | Code-confirmed | none | PR | Merged 2026-10-17 into 2.18.3 (474a1f2de) | PR [HTND#52](https://github.com/HoosatNetwork/HTND/pull/52) |

## Summary

`deploy/htnd.service` sets `TimeoutStopSec=300` and `KillSignal=SIGINT`; the unit in
`docs/running-a-node-in-ubuntu.md` has neither (systemd default 90 s), while the node's outer shutdown timeout is 120 s
and includes the 90 s event drain. A SIGKILL mid-drain forces a UTXO-index rebuild at the next start.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `deploy/htnd.service:41`; `docs/running-a-node-in-ubuntu.md:155-166`

## Impact

Operators following the guide get SIGKILLed shutdowns whenever the event drain is slow, and a slow restart afterwards
because the UTXO index must be rebuilt from consensus. The kill does not corrupt the database (per-block commits are
atomic), but it widens the window of HTN-02 and hides the root cause of a slow shutdown (HTN-06).

## Evidence

Files read. The shutdown budget was corrected by the second review: an earlier internal figure of "~210 s" was wrong;
the outer timeout is 120 s and includes the 90 s drain. `KillSignal=SIGINT` matters because the node handles SIGINT and
SIGTERM identically but the shipped unit chooses SIGINT.

## Recommendation

Add `TimeoutStopSec=300` and `KillSignal=SIGINT` to the documented unit.

## Verification

**Completed:** files read.

**Required before submission:** none (documentation change).

## Chain impact

None.

## Related items

[HTN-05](HTN-05.md)

## Upstream

PR [HTND#52](https://github.com/HoosatNetwork/HTND/pull/52) — in review.

_AI disclosure: prepared with AI assistance (Claude by Anthropic; cross-reviewed with OpenAI Codex)._
