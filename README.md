# Gibson Caretaker Services

The website and contact form for **Gibson Caretaker Services** — gentle yard, garden, and home help for older and busy neighbors in and around Darlington, WI.

Live site: **https://gibsoncaretakerservices.com**

## What this is

A single [Cloudflare Worker](https://developers.cloudflare.com/workers/) that does two jobs:

- **Serves the website** — the static `public/` folder, which is one self-contained `index.html` (no libraries, no build step), delivered through the Worker's [static-assets binding](https://developers.cloudflare.com/workers/static-assets/).
- **Handles the contact form** — `POST /api/contact`. Each submission runs through a small pipeline (below) and ends with an email to the business inbox containing a one-tap "Add to calendar" link (Google Calendar) and an `.ics` attachment (Apple/Outlook). Sending is free because mail goes only to the owner's own verified address via [Cloudflare Email Routing](https://developers.cloudflare.com/email-routing/email-workers/).

The direct **call/text** path on the site is plain `tel:`/`sms:` links — phone-to-phone, with no dependency on the Worker, so it keeps working even if everything server-side is down.

### Contact form pipeline

For each `POST /api/contact` submission, `src/index.js` runs:

```
honeypot  →  validate (name + phone required)  →  Turnstile spam gate  →  save to D1  →  email the owner
```

The lead is written to the database **before** the email is sent, so a request is not lost even if the email fails.

Two of these stages are **optional and self-guarding** — until you configure them, the form behaves as a simple honeypot-protected emailer:

- **Spam gate** — only enforced when the `TURNSTILE_SECRET` secret is set. Without it, `verifyTurnstile` returns `true` and the honeypot is the only bot defense.
- **Lead backup (D1)** — only used when the `DB` binding exists. Without it, `saveLead` skips silently and the form just emails.

## Endpoints

| Route | Method | Behavior |
|---|---|---|
| `/api/contact` | `POST` | Handles a form submission (pipeline above). Returns JSON. |
| `/api/leads` | `GET` | Private HTML view of saved leads. Returns `404` unless the `ADMIN_KEY` secret is set **and** a matching `?key=` is supplied. |
| everything else | `GET` | Served from `public/` via the `ASSETS` binding. |

## Tech stack

- **Runtime:** Cloudflare Workers (`compatibility_date` 2025-09-01, `nodejs_compat`)
- **Email:** Cloudflare Email Routing via the `cloudflare:email` binding, with [`mimetext`](https://www.npmjs.com/package/mimetext) to build the MIME message
- **Database:** Cloudflare D1 (SQLite) — schema in `migrations/0001_init.sql`
- **Spam protection:** honeypot field + Cloudflare Turnstile
- **Tooling:** Wrangler 4
- **Frontend:** a single hand-written `public/index.html` — no framework, no build step

## Project structure

```
.
├── public/
│   └── index.html                      # the whole website (no libraries, no build step)
├── src/
│   └── index.js                        # the Worker: serves the site, spam gate, lead backup, email
├── migrations/
│   └── 0001_init.sql                   # the lead-backup database table (D1)
├── scripts/
│   └── set-phone.mjs                   # one-command phone-number swap across the site
├── wrangler.jsonc                      # Cloudflare config (asset + email + D1 bindings)
├── package.json
├── HANDOFF.md                          # complete, start-to-finish deploy guide — START HERE
├── SETUP.md                            # email + site basics (detail)
├── SETUP-leadbackup-and-spamgate.md    # D1 + Turnstile detail
├── THE-ENDGAME-flow-and-reliability.md # design rationale
├── CLAUDE-CODE-PROMPT.md               # the prompt used to drive an agent-assisted deploy
├── LICENSE
└── README.md
```

## Setup and deploy (quick version)

> The complete, start-to-finish guide is **`HANDOFF.md`** — it covers email authentication, the spam gate, the lead backup, account hardening, and a test checklist. The short version:

```bash
npm install
npx wrangler login          # opens the browser, logs into your Cloudflare account
npx wrangler deploy         # publishes the Worker to a *.workers.dev URL
```

Then, in the Cloudflare dashboard, add the domain as a Custom Domain on the Worker, and turn on **Email Routing** for the domain with the destination Gmail verified (see `SETUP.md`).

To create and migrate the lead-backup database:

```bash
npx wrangler d1 create gibson-leads        # prints a database_id for wrangler.jsonc
npm run db:init                            # applies migrations/0001_init.sql to the remote DB
```

## Configuration, secrets, and PII

This is a **public** repository. Secrets are never committed — they live in Cloudflare and in local files that `.gitignore` excludes.

- **Worker secrets** are set with Wrangler and stored by Cloudflare, never in the repo:

  ```bash
  npx wrangler secret put TURNSTILE_SECRET   # enables the Turnstile spam gate
  npx wrangler secret put ADMIN_KEY          # enables the private /api/leads view
  ```

- **Local development** uses a `.dev.vars` file for the same values — it is gitignored. (No `.dev.vars.example` is shipped; the two variables above are the full set.)
- **In-code values** in `src/index.js` and `wrangler.jsonc` are not secrets: the `FROM`/`TO` email addresses and the D1 `database_id` are public identifiers. The D1 `database_id` is meaningless without account authentication.
- **Phone number:** the site ships with the placeholder `(608) 555-5555`. Set the real number — ideally a Google Voice number, to keep a personal cell private — with `node scripts/set-phone.mjs <10-digit-number>`, then redeploy. No real personal phone number is committed.
- The `/api/leads` view exposes saved names and phone numbers, so the `ADMIN_KEY` link must be kept private.

## Editing the site

Everything visible is in `public/index.html`. Edit it, then run `npx wrangler deploy` again (or, if you connect this repo to Cloudflare, push to the connected branch).

## License

[MIT](./LICENSE)
