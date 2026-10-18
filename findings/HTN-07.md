# HTN-07 — Pebble logger adapter: `Fatalf` returns instead of terminating

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Medium | storage | Reproduced | none | PR | Draft — not yet submitted | TBD |

## Summary

`pebbleLoggerAdapter.Fatalf` logs and returns; Pebble requires it to terminate. With `HTND_PEBBLE_LOG_EVENTS` set,
a fatal commit error is logged and the commit is reported successful.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `infrastructure/db/database/pebble/pebble_logger_adapter.go:18-20`
- Installed when `HTND_PEBBLE_LOG_EVENTS` is set (`options.go:215-221`)

## Impact

Opt-in path only, but on it the node acknowledges writes that never happened and continues with a database whose
MANIFEST may be stale; MANIFEST flush and sync failures are swallowed the same way (`version_set.go:191-202`). Because
the operator enabled the adapter to get *more* diagnostics, the failure mode is counter-intuitive: the extra logging
makes a fatal error non-fatal. It is also a prerequisite for any future sync point (HTN-27), since a sync error must
terminate the process to be meaningful.

## Evidence

- `TestS1PebbleFatalfDoesNotReturn`: with an injected WAL-sync EIO, `Set(..., Sync)` returned nil. The control with
  Pebble's default logger exits 1 with "pebble: fatal commit error: input/output error".
- Code: Pebble's `applyInternal` returns nil after calling `Fatalf` (`db.go:882-897`).

## Recommendation

`Fatalf` -> Critical log followed by `panics.Exit`, matching Pebble's contract and the behaviour of its default
logger. Three-line change, no format or configuration change. Target: master + v2.18.1.

## Verification

**Completed:** `TestS1PebbleFatalfDoesNotReturn` fails before and passes with the prototype; the default-logger control passes.

**Required before submission:** the test included in the PR with its fault-injection fixture.

## Chain impact

None (node-local).

## Related items

[HTN-27](HTN-27.md), [HTN-03](HTN-03.md)

## Upstream

TBD — PR/issue link to be filled in once submitted.

