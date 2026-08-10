# Recovery runbook (variant search)

## Goal
Find and restore the exact intended live variant using objective markers, not guesswork.

## Recovery sequence
1. Enumerate candidate files by timestamp from:
   - repo `public/`
   - `backups/`
   - known local snapshot folders
2. Build a marker matrix for each candidate:
   - request form marker (`rq-form` or `contact-form`)
   - iMessage preview marker
   - neighbor proof marker set
   - portrait/frame markers
3. Select the highest-confidence candidate and restore it to `public/index.html`.
4. Restore its required assets.
5. Run:
   ```bash
   npm run verify:preflight
   npm run deploy:safe
   ```

## Required evidence before declaring recovery complete
- Candidate path recorded
- Marker matrix recorded
- Both live URLs pass post-deploy parity check
