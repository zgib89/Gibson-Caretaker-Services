# Deploy runbook (safe path)

## Canonical rule
Deploy only with release guards enabled.

## Commands
```bash
npm install
npm run verify:preflight
npm run deploy:safe
```

`deploy:safe` runs:
1. local preflight marker/asset validation
2. `wrangler deploy`
3. workers.dev + custom-domain post-deploy parity validation

If manifest ownership state is `blocked`, preflight will fail until ownership migration is resolved:

- `docs/runbooks/OWNERSHIP-MIGRATION.md`

## Canonical release profile
- Manifest:
  - `backups/live-baselines/2026-07-27-index-now/manifest.json`
- Guard script:
  - `scripts/release/verify-release-profile.mjs`

## Do not
- Do not deploy from ad-hoc or unverified local variants.
- Do not skip post-deploy verification.
