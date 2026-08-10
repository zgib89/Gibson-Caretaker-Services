# Incident record: live version mismatch and recovery (2026-08-10)

## What happened
A deploy went live from the wrong local variant, which replaced the expected production experience with an older/different site version.

## User-visible impact
- The expected combination of:
  - barnwood/framed portrait treatment
  - iMessage-style proof preview
  - request form variant
  - three neighbor proof photos
  was not consistently present on live.

## Root cause
- Multiple local variants existed across worktrees, backups, and snapshots.
- There was no enforced canonical release profile before deploy.
- Deploys were possible without marker/asset verification against a known-good baseline.

## Recovery source of truth
Recovered canonical snapshot source:

`C:\Users\zacgi\Gibson-Caretaker-Services\live-snapshot\index-now.html`

## Recovery actions performed
1. Compared candidate variants by marker set.
2. Restored the canonical snapshot profile and required assets.
3. Redeployed and verified marker presence on both worker URL and custom domain.

## Preventive controls required
1. Manifested canonical release profile with required markers/assets.
2. Pre-deploy validation that blocks deployment on profile mismatch.
3. Post-deploy parity verification (workers.dev and custom domain).
4. Structured runbook for release/rollback/recovery.
5. Explicit ownership migration control for custom-domain-to-service binding.

## Ownership migration finding
- Current known split:
  - deploy target service: `gibson-caretaker-services`
  - custom-domain bound service: `gibson-caretaker-web`
- This is now tracked as a blocked migration and must be resolved with:
  - `docs/runbooks/OWNERSHIP-MIGRATION.md`

## Policy
Do not deploy from an unverified variant.  
Only deploy when the canonical release profile check passes.
