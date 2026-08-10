# Rollback runbook

## Trigger
Use rollback when live markers fail post-deploy checks or the user reports a variant mismatch.

## Rollback steps
1. Restore canonical baseline:
   - `backups/live-baselines/2026-07-27-index-now/index.html`
2. Ensure required assets from manifest exist in `public/`.
3. Run:
   ```bash
   npm run verify:preflight
   npm run deploy:safe
   ```
4. Confirm both URLs pass marker checks.

## Verification endpoints
- Workers URL:
  - `https://gibson-caretaker-services.zacgibson89.workers.dev`
- Custom domain:
  - `https://gibsoncaretakerservices.com`
