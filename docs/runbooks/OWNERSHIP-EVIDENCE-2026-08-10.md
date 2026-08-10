# Ownership evidence snapshot (2026-08-10)

Purpose: preserve pre-cutover evidence for custom-domain routing, cache behavior, service versions, and binding differences.

## Service/version preservation

- `gibson-caretaker-services`
  - version: `e81dfda5-bd1f-4f32-adcb-8e1b07d94113`
  - compatibility date: `2025-09-01`
  - bindings:
    - `assets:ASSETS`
    - `d1:DB:31695289-8e23-4a75-8b13-c094816a2d6b`
    - `secret_text:ADMIN_KEY`
    - `send_email:MAIL:gibsoncaretakerservices@gmail.com`

- `gibson-caretaker-web`
  - version: `7dea095b-df71-40e0-853a-e12e6328a973`
  - compatibility date: `2026-07-01`
  - bindings:
    - `assets:ASSETS`
    - `d1:DB:31695289-8e23-4a75-8b13-c094816a2d6b`
    - `secret_text:ADMIN_KEY`
    - `secret_text:RESEND_API_KEY`

## Endpoint header/cache capture

Captured using `Invoke-WebRequest` for GET `/`:

### `https://gibsoncaretakerservices.com`
- `cf-cache-status: HIT`
- `cache-control: public, must-revalidate, max-age=0`
- `content-security-policy`: (matches `gibson-caretaker-services` profile)

### `https://www.gibsoncaretakerservices.com`
- `cf-cache-status: HIT`
- `cache-control: public, must-revalidate, max-age=0`
- `content-security-policy`: (matches `gibson-caretaker-services` profile)

### `https://gibson-caretaker-services.zacgibson89.workers.dev`
- `cf-cache-status: HIT`
- `etag: W/"bda9755324d54ccb6e59606be5ed7be9"`
- `cache-control: public, must-revalidate, max-age=0`
- marker signature includes `ba-garden.png`, `ba-container.png`, `ba-chairs.png`

### `https://gibson-caretaker-web.zacgibson89.workers.dev`
- `cf-cache-status: HIT`
- `etag: W/"241ae2dd32b92e73f77b79c8a4885f55"`
- `cache-control: public, must-revalidate, max-age=0`
- marker signature does not include `ba-*` markers and includes `RESEND`

## Interpretation

The workers.dev endpoints currently show different marker signatures between services while custom domains appear aligned with the `gibson-caretaker-services` signature.  
This supports keeping migration in a **blocked** state until ownership/routing behavior is explained and validated through a controlled cutover plan.
