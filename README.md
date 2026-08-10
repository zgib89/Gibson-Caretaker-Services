# Gibson Caretaker Services

The website + contact form for **Gibson Caretaker Services** — gentle yard, garden, and home help for older and busy neighbors in Darlington, WI.

Live site: **https://gibsoncaretakerservices.com**

## Release safety (required)

Use the guarded deployment path so the wrong local variant cannot be deployed:

```bash
npm run deploy:safe
```

This runs preflight validation, deploys, then verifies workers.dev/custom-domain parity.

- Guard script: `scripts/release/verify-release-profile.mjs`
- Canonical profile: `backups/live-baselines/2026-07-27-index-now/manifest.json`
- Runbooks: `docs/runbooks/DEPLOY.md`, `docs/runbooks/ROLLBACK.md`, `docs/runbooks/RECOVERY.md`

### Ownership migration status

Release guard currently marks domain ownership migration as **blocked** until custom domains and canonical Worker service ownership are resolved:

- Runbook: `docs/runbooks/OWNERSHIP-MIGRATION.md`
- Temporary bypass for emergency commands only: `RELEASE_GUARD_ALLOW_BLOCKED_OWNERSHIP=1`

## What this is

A single Cloudflare Worker that:

- **Serves the website** (the `public/` folder — one self‑contained `index.html`).
- **Handles the contact form** at `POST /api/contact`: it emails Mariah each request with a one‑tap "Add to calendar" link (Google) and an `.ics` attachment (Apple/Outlook). Sending is **free** because mail only goes to her own verified address.

```
.
├── public/
│   └── index.html                     # the whole website (no libraries, no build step)
├── src/
│   └── index.js                       # the Worker: serves the site, spam gate, lead backup, email
├── migrations/
│   └── 0001_init.sql                  # the lead-backup database table
├── scripts/
│   └── set-phone.mjs                  # one-command phone-number swap
├── wrangler.jsonc                     # Cloudflare config (asset + email + D1 bindings)
├── package.json
├── HANDOFF.md                         # ⭐ the complete, do-everything deploy guide — START HERE
├── SETUP.md                           # email + site basics (detail)
├── SETUP-leadbackup-and-spamgate.md   # D1 + Turnstile detail
├── THE-ENDGAME-flow-and-reliability.md# the design rationale
└── README.md
```

## Deploy (quick version)

> ⭐ **The complete, start-to-finish deployment guide is `HANDOFF.md`.** It covers everything below plus email auth, the spam gate, the lead backup, security hardening, and a test checklist. The quick version is here:

```bash
npm install
npx wrangler login          # opens the browser, logs into your Cloudflare account
npm run deploy:safe         # guarded deploy + post-deploy parity verification
```

Then in the Cloudflare dashboard, add **gibsoncaretakerservices.com** as a Custom Domain on the Worker.

The contact form needs **Email Routing** turned on for the domain, with
`gibsoncaretakerservices@gmail.com` verified as a destination — see SETUP.md.

## Edit the site

Everything visible is in `public/index.html`. Change it, then run `npm run deploy:safe`
again (or, if you connect this repo to Cloudflare, deploy from verified CI).
