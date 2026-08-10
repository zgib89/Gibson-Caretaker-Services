# Cloudflare ownership migration (blocked)

## Current blocked state
- Repository deploys target Worker service: `gibson-caretaker-services`
- Custom domains are currently bound to Worker service: `gibson-caretaker-web`
- Preserve rollback target for current custom-domain owner:
  - `7dea095b-df71-40e0-853a-e12e6328a973`

Because of this split, marker parity can look correct while ownership is still wrong for release safety.

## Policy
Do **not** rebind domains until this migration runbook is executed end-to-end with rollback safety.

## Migration sequence (rollback-safe)
1. Determine canonical Worker service to own both custom domains.
2. Compare candidate services side-by-side (content markers + behavior + form flow).
3. Capture rollback targets (current version IDs for both services).
4. Rebind both custom domains to canonical service in one controlled cutover window.
5. Validate workers.dev + custom-domain parity and ownership after cutover.
6. Update baseline manifest ownership section from `blocked` to `verified`.

## Mandatory decision gate: MAIL vs RESEND

Do not cut over until this is explicitly decided and documented:

- Option A: canonical service keeps `MAIL` (`send_email`) as production email path.
- Option B: canonical service keeps `RESEND_API_KEY` as production email path.

Rules:
1. Preserve both existing services/versions unchanged until decision is approved.
2. Do not silently drop `MAIL` or `RESEND_API_KEY` during migration.
3. Record final chosen mail path and corresponding rollback instruction in this runbook before rebinding.

## Current service comparison snapshot

### Deployment/version
- `gibson-caretaker-services`: `e81dfda5-bd1f-4f32-adcb-8e1b07d94113` (2026-08-10)
- `gibson-caretaker-web`: `7dea095b-df71-40e0-853a-e12e6328a973` (2026-07-27)

### Binding differences (unique)
- `gibson-caretaker-services` includes `MAIL` (`send_email`) and does **not** include `RESEND_API_KEY`.
- `gibson-caretaker-web` includes `RESEND_API_KEY` and does **not** include `MAIL`.
- Both include `ASSETS`, `DB`, and `ADMIN_KEY`.

### Content/asset signature differences (workers.dev endpoints)
- `gibson-caretaker-services` workers.dev currently includes `ba-garden.png`, `ba-container.png`, `ba-chairs.png`.
- `gibson-caretaker-web` workers.dev currently does not include those `ba-*` markers and does include `RESEND` marker text.

## Cache/asset-routing evidence capture

Header/cache evidence is tracked in:

- `docs/runbooks/OWNERSHIP-EVIDENCE-2026-08-10.md`

Use fresh captures immediately before any rebinding change.

## Temporary bypass
The release guard blocks preflight/postdeploy when ownership is `blocked`.

Bypass is explicit and temporary:

```bash
RELEASE_GUARD_ALLOW_BLOCKED_OWNERSHIP=1 npm run verify:preflight
```

Use bypass only for emergency operations while migration remains blocked.
