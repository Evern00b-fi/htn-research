# HTN-26 — WAL can be disabled by environment variables without any log line

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Low | storage | Reproduced | none | PR | Draft — not yet submitted | TBD |

## Summary

`HTND_PEBBLE_DISABLE_WAL` and `HTND_TEST_MODE` silently disable the WAL. `HTND_TEST_MODE` also bypasses an RPC check,
so it is easy to set on a real node; a process crash then loses every write since the last flush.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `infrastructure/db/database/pebble/options.go:122`; `app/rpc/rpchandlers/get_block.go:67`

## Impact

Silent loss of durability on misconfigured nodes: a process crash then loses every write since the last memtable
flush (with the default options up to eight 64 MiB memtables; the options are configurable), although the result
stays prefix-consistent because flushes are ordered. Commit `8cb30f9c0` briefly disabled the WAL by default and
`7148270f0` reverted it; no tag shipped with the WAL off, so the exposure today is limited to operators who set one of the variables.

## Evidence

`TestS1ProcessCrashWithAndWithoutWAL`: a committed transaction survives with the WAL and is lost with either variable set.

## Recommendation

Log a warning at open when `DisableWAL` is set (one line). Later, as a separate change, stop deriving the WAL setting
from `HTND_TEST_MODE`, since that variable also has unrelated RPC effects; CI that sets it would then write a WAL.

## Verification

**Completed:** `TestS1ProcessCrashWithAndWithoutWAL`.

**Required before submission:** a log assertion in the open test.

## Chain impact

None (node-local).

## Related items

[HTN-27](HTN-27.md)

## Upstream

TBD — PR/issue link to be filled in once submitted.

