# HTN-28 — Release authentication and updater verification need completion

| Severity | Category | Evidence level | Chain impact | Proposed action | Status | Upstream |
|---|---|---|---|---|---|---|
| Low | process | Code-confirmed | none | Issue | Draft — not yet submitted | TBD |

## Summary

The release workflow generates SHA-1 checksum files next to each archive; signed release metadata is not
established, and the opt-in auto-updater expects a signed checksum list for which no key is configured. SHA-1 is
adequate for download-integrity checks but is not a signature and is not collision-resistant.

## Affected code

Paths and lines refer to HTND `a56566e86` (branch v2.18.1) unless stated otherwise.

- `.github/workflows/deploy.yaml:53, 73-74, 88` (`sha1sum` per archive; the asset-upload list at `:96` carries an inline
  comment inside the multi-line string, so whether the checksum files are actually uploaded is unverified here)
- `.github/workflows/deploy.yaml:66` (`-trimpath` on the Windows build; not shown for every platform)
- `infrastructure/autoupdate/config.go:86-88` (expects a signed checksum list; no key)

## Impact

Operators can check that a download is intact if the checksum assets are published, but cannot verify who built
it, and the updater cannot verify releases as designed. For a project whose releases schedule hard forks, verifiable
binaries are part of the activation process (HTN-14).

## Evidence

Workflow and updater configuration read at a56566e86. Actual upload of the checksum assets was not verified (no
GitHub access during this review). The updater is opt-in and off by default, so nothing is broken for operators today.

## Recommendation

Options: (a) do nothing; (b) publish SHA-256 sums for every asset, sign the checksum list (minisign or cosign), set
the updater key, and apply `-trimpath` uniformly for reproducible builds. Recommendation: (b). Decision requested:
approve and choose the signing tool?

## Verification

**Completed:** workflow and updater configuration read.

**Required before submission:** confirm on a published release whether the checksum assets are uploaded; a release
carries sums and a signature; the updater verifies them.

## Chain impact

None.

## Related items

[HTN-14](HTN-14.md)

## Upstream

TBD — PR/issue link to be filled in once submitted.

