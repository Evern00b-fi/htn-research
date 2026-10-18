# HTN-15 — Block acceptance in relay depends on a transport field the block hash does not commit to

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Medium | P2P | Code-confirmed | none / P2P version | Issue | Draft — not yet submitted | TBD |

## Summary

`DomainBlock.PoWHash` is a string outside the header and not part of the block hash. For block version >= 4, relay
validation requires the field and rejects a block whose field is empty or differs from the node's own recomputation;
IBD bodies are validated with `powSkip=true`, ignoring it. Relay does not forward a block lacking the field, and the
peer-penalty policy around it requires mixed-version compatibility testing. The field crosses validation, transport
and caching code but is omitted from database serialisation. The node computes the PoW value itself in every path.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `domain/consensus/utils/pow/pow.go:205-217` (comparison), `domain/consensus/model/externalapi/block.go`
- Relay vs IBD: `handle_relay_invs.go` (`powSkip=false`), `ibd.go:870` (`powSkip=true`)

## Impact

A block's acceptance in relay depends on transport metadata rather than on the block itself; nodes that drop the
field would not interoperate with older peers unless they fill it when relaying.

## Evidence

Code read at a56566e86; the "stored in the database" claim was refuted by the second review (serialisation omits
the field; the block-cache regression test confirms its loss after eviction).

## Recommendation

Options: (a) retain the requirement; (b) node-local relaxation, no fork: accept a block without the field (as IBD
does), do not penalise absence, and fill the field from the node's own value when relaying so older peers still accept;
(c) later, drop the field from the wire format at the next P2P protocol version. Recommendation: investigate (b),
subject to mixed-version tests. What the field protected (early rejection of miners whose PoW implementation diverges)
can be kept pool-side; the bridge recomputes every share.

## Verification

**Completed:** code read; the 'stored in the database' claim refuted by the existing block-cache test.

**Required before submission:** mixed-version tests: absent, malformed and mismatching field, old and new node in each role.

## Chain impact

(b) none (node-local acceptance plus relay normalisation); (c) P2P protocol version. No block becomes invalid retroactively.

## Related items

[HTN-37](HTN-37.md), [HTN-16](HTN-16.md)

## Upstream

TBD — PR/issue link to be filled in once submitted.

