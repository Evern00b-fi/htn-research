# HTN-44 — Bridge: the template cache is no longer cleared on a new-block notification

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Low | tooling | Measured | none | PR | Merged 2026-10-17 into 1.8.2 (6e4af6a5d) | PR [bridge#9](https://github.com/HoosatNetwork/htn-stratum-bridge/pull/9) |

## Summary

Commit `d578817` cleared the GetBlockTemplate cache when the node announced a new block, so miners immediately got a
job built on the new tips. One day later `b9e62cb` ("Add support for --mine-when-not-synced") rewrote
`startBlockTemplateListener` and the `invalidateGBTCache()` call was dropped. A notification that arrives within the
cache TTL (`gbt_cache_ttl`, 190 ms by default) now re-sends the cached template, so miners keep building on parents
that are already superseded.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `htn-stratum-bridge/src/htnstratum/htnapi.go` (`startBlockTemplateListener`, `blockReadyChan` case) @3b2cf8c
- History: `git log -S "invalidateGBTCache()" -- src/htnstratum/htnapi.go`

## Impact

Fresher jobs for every miner behind a bridge. Missing known tips go with red blocks across the network
([reports/red-blocks.md](../reports/red-blocks.md), R3), but a reduction of the red rate from this fix has **not** been
demonstrated.

## Evidence

Pre-registered before/after comparison on one private solo bridge (about 9 h before, about 6 h after, 15 minutes
after each pruning-point move excluded; Wilson 95 % intervals):

| Metric (own miner) | Before | After |
|---|---|---|
| A tip the node already knew is missing from the parents | 46.7 % [44.8, 48.7] (1154/2469) | 8.5 % [7.3, 10.0] (144/1689) |
| Same, tip at least 50 ms old | 32.2 % (795/2469) | 0.18 % (3/1689) |
| Red share | 2.07 % [1.57, 2.71] | 0.95 % [0.58, 1.53] |
| Red share, all other miners (control) | 8.05 % | 6.78 % |

The mechanism criterion is met (z = −31.5). The red-rate criterion is not: the pre-registered difference-in-differences
is +0.15 pp, 95 % CI [−0.61, +0.91], because the network's red share fell at the same time. An exploratory,
not pre-registered relative-risk ratio is 0.54 [0.31, 0.95]; it needs confirmation in a new pre-registered window.

![Two panels. Left: share of own blocks missing a known tip fell from 46.7 % to 8.5 %, and with a tip at least 50 ms old from 32.2 % to 0.18 %. Right: red share of own blocks 2.07 % to 0.95 % and of other miners 8.05 % to 6.78 %, with overlapping change; marked not significant under the pre-registered difference-in-differences.](../figures/gbt-cache-before-after.svg)

## Recommendation

Restore the call at the start of the `blockReadyChan` case, as in `d578817`; one line plus a comment. The PR claims
fresher jobs, not fewer red blocks. Independently, `gbt_cache_ttl: 0` disables the cache.

## Verification

**Completed:** history read; build, `gofmt`, `git diff --check` clean; live before/after above.

**Required before submission:** a listener seam and behavioural test if maintainers want one (the listener needs a
live RPC client today).

## Chain impact

None (pool software).

## Related items

[HTN-20](HTN-20.md), [HTN-32](HTN-32.md), [HTN-04](HTN-04.md)

## Upstream

PR [bridge#9](https://github.com/HoosatNetwork/htn-stratum-bridge/pull/9) — in review.

