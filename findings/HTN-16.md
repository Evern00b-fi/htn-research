# HTN-16 — Deterministic FP64 PoW: keep ASIC resistance, remove platform dependence

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Medium | consensus | Hypothesis | version-gated forward fork | Issue | Draft — not yet submitted | TBD |

## Summary

After HTN-01 removes fusion, HoohashV110 still calls `math.Exp/Sin/Cos` (Go) or glibc libm (linux/arm64 C path).
These are not bit-identical across implementations, and Go's `Exp` picks an FMA path at run time on amd64. A flip
needs a product within about 1 ulp of a boundary: rare, but structural. Hoohash is FP64-heavy on purpose so that small
actors and ARM devices can mine; integer-only PoW is **not** proposed.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `domain/consensus/utils/pow/heavyhash.go:133-167, 446-447`
- `pow_aarch64_linux.go` (C path, libm)

## Impact

A rare platform-dependent PoW disagreement would orphan valid blocks on some builds.

## Evidence

- 1 M inputs, arm64 vs amd64 (non-FMA path): `Exp` differs in the last bit in 37 % of cases, `Sin`/`Cos` in 1 %.
- No output difference observed in 3000 PoW samples after the HTN-01 patch; output impact therefore remains a hypothesis.
- Precedent: RandomX is ASIC-resistant and floating-point heavy yet cross-platform deterministic by using only
  correctly-rounded IEEE-754 basic operations in a fixed order and no libm.

## Recommendation

Options: (a) do nothing beyond HTN-01 and cross-architecture vectors (HTN-24); (b) at a future fork keep FP64,
forbid fusion, restrict to correctly-rounded basic operations in a fixed order and replace `sin/cos/exp/log` with
deterministic in-tree implementations, version-gated. Recommendation: (a) now; study (b) together with HTN-04.

## Verification

**Completed:** 1 M-input libm comparison; 3000-sample PoW comparison after the HTN-01 patch (no output difference).

**Required before submission:** cross-platform golden vectors (amd64 with and without FMA, arm64 Go and C paths) in CI; any (b) change ships with a new vector set.

## Chain impact

(b) forward hard fork, version-gated; existing blocks keep their current PoW evaluation. No rewind.

## Related items

[HTN-01](HTN-01.md), [HTN-24](HTN-24.md), [HTN-25](HTN-25.md)

## Upstream

TBD — PR/issue link to be filled in once submitted.

