# Gibson Caretaker Services — Complete Handoff & Deployment Guide

This is the one document that takes the project from this folder to **fully live and airtight**. Work top to bottom. Every step is labeled:

- **`[CODE]`** — a terminal command or file edit (Claude Code can do these).
- **`[BROWSER]`** — a click in the Cloudflare or Google dashboard (a human must do these; an agent can't log into a dashboard).

Nothing here costs money beyond the domain (~$10/yr) and the existing $5/mo Cloudflare Workers plan.

---

## 0. What you're deploying

A single Cloudflare Worker that:
- **serves the website** (`public/index.html` — one self-contained file, no build step),
- **handles the contact form** (`POST /api/contact`): honeypot → spam gate (Turnstile) → **saves the lead to a database (D1)** → emails Mariah with a one-tap "Add to calendar" link + `.ics`,
- **keeps a private, recoverable list** of every request (`/api/leads`, key-protected).

The call/text path is **pure phone-to-phone** — it has no dependency on any of the above, so it works even if everything server-side is down.

### Current state
- ✅ Site, funnel, logo, pricing, FAQ, schema, accessibility — **done & validated**.
- ✅ Worker with spam gate + lead backup — **built, self-guarding** (works before setup, activates after).
- ⏳ Phone is the placeholder **(608) 555-5555** — swap before sharing the public link.
- ⏳ Not yet deployed; email auth, Turnstile, D1, security hardening = the steps below.

---

## 1. Reference values (use these exactly)

| Thing | Value |
|---|---|
| Domain | `gibsoncaretakerservices.com` |
| Public site | `https://gibsoncaretakerservices.com` |
| Worker name | `gibson-caretaker-services` |
| Owner inbox (form lands here) — `TO` | `gibsoncaretakerservices@gmail.com` |
| Branded sending address — `FROM` | `mariah@gibsoncaretakerservices.com` |
| Phone in code right now | `(608) 555-5555` → swap with `set-phone.mjs` |
| Worker bindings | `ASSETS` (site), `MAIL` (email), `DB` (D1, after step 8) |
| Worker secrets | `TURNSTILE_SECRET` (spam gate), `ADMIN_KEY` (optional leads view) |
| Front-end key | `TURNSTILE_SITEKEY` in `public/index.html` |

---

## 2. Prerequisites

- **`[BROWSER]`** A Cloudflare account that owns `gibsoncaretakerservices.com` and has the $5/mo Workers Paid plan.
- **`[BROWSER]`** Access to the Google account behind `gibsoncaretakerservices@gmail.com`.
- **`[CODE]`** Node.js LTS installed (`node -v` ≥ 18).

---

## 3. Install

**`[CODE]`**
```bash
cd gibson-caretaker-services
npm install
```

---

## 4. Put it on GitHub (optional but recommended)

**`[BROWSER]`** Create an **empty** repo named `gibson-caretaker-services` (no README/license).
**`[CODE]`**
```bash
git init
git add -A
git commit -m "Gibson Caretaker Services — site + worker"
git branch -M main
git remote add origin https://github.com/<your-username>/gibson-caretaker-services.git
git push -u origin main
```
> The repo is safe to make public — there is **no personal phone number or secret in the code** (the phone is a placeholder; all secrets live in Cloudflare, never in files).

---

## 5. First deploy (to a test URL)

**`[CODE]`**
```bash
npx wrangler login      # opens the browser once to authorize
npx wrangler deploy
```
This publishes to a temporary `https://gibson-caretaker-services.<subdomain>.workers.dev` URL. Open it — the site should load fully. (The form won't email yet until step 6; that's expected.)

---

## 6. Email — inbox + the address the form sends from

**`[BROWSER]`** Cloudflare dashboard → your domain → **Email → Email Routing → Get started**.
1. **Destination address:** add `gibsoncaretakerservices@gmail.com`. Cloudflare emails a verification link — **click it.** It must show **Verified**.
2. **Custom address:** create `mariah@gibsoncaretakerservices.com` → forward to the verified inbox.
3. (Optional) enable **Catch-all** → the verified inbox.

Enabling Email Routing **automatically adds the MX, SPF, and DKIM DNS records** for you. ✅

> `FROM` (`mariah@…`) and `TO` (the verified Gmail) are already set in `src/index.js` and `wrangler.jsonc`. That pairing is what makes sending **free**. Only change them if the domain or inbox differs.

---

## 7. Email authentication (so mail lands and can't be spoofed)

Email Routing added SPF + DKIM in step 6. **Add the one record it doesn't: DMARC.**

**`[BROWSER]`** Cloudflare → your domain → **DNS → Records → Add record**:

| Field | Value |
|---|---|
| Type | `TXT` |
| Name | `_dmarc` |
| Content | `v=DMARC1; p=none; rua=mailto:gibsoncaretakerservices@gmail.com; fo=1` |

> ⚠️ **Do not add a second SPF record** — Cloudflare already made one (`v=spf1 include:_spf.mx.cloudflare.net ~all`). Two SPF records break SPF. Leave it alone.
>
> Start at `p=none` (monitor only). After a week or two with clean reports, tighten to `p=quarantine; pct=100`.

---

## 8. Set the real phone number

Do this **before** sharing the public link, so no one ever taps a dead number.

**`[BROWSER]`** Create a free **Google Voice** number (voice.google.com) with a local 608 area code, forwarded to Mariah's cell. *Reply to customers from the Voice app* so her personal number stays private.

**`[CODE]`** Put that number everywhere in one shot:
```bash
node scripts/set-phone.mjs 6085551234     # ← the Google Voice number, 10 digits
```

---

## 9. Spam gate — Turnstile (free, stops bots)

**`[BROWSER]`** Cloudflare → **Turnstile → Add widget**: name `gibson-form`, domain `gibsoncaretakerservices.com`, mode **Managed**. Copy the **Site Key** and **Secret Key**.

**`[CODE]`**
1. In `public/index.html`, set the site key:
   ```js
   var TURNSTILE_SITEKEY='0x4AAAAAAA...yourSITEkey...';
   ```
2. Store the secret (paste when prompted):
   ```bash
   npx wrangler secret put TURNSTILE_SECRET
   ```

---

## 10. Lead backup — D1 (free, no request ever lost)

**`[CODE]`**
```bash
npx wrangler d1 create gibson-leads
```
It prints a `database_id`. In `wrangler.jsonc`, **uncomment** the `d1_databases` block at the bottom (including the leading comma) and paste the id. Then create the table:
```bash
npm run db:init        # = wrangler d1 execute gibson-leads --remote --file=migrations/0001_init.sql
```

### (Optional) private view of saved requests
**`[CODE]`**
```bash
npx wrangler secret put ADMIN_KEY     # paste a long random password
```
Then the list lives at `https://gibsoncaretakerservices.com/api/leads?key=YOUR_ADMIN_KEY`. Without the key it returns "Not found." Keep the link private (it shows names + phones).

---

## 11. Redeploy with everything on

**`[CODE]`**
```bash
npx wrangler deploy
```

---

## 12. Point the domain at the site

**`[BROWSER]`** Cloudflare → **Workers & Pages → `gibson-caretaker-services` → Settings → Domains & Routes → Add → Custom domain** → `gibsoncaretakerservices.com` (add `www.` too). Live in a few minutes.

---

## 13. Lock the accounts (do not skip — this protects Mariah)

**`[BROWSER]`**
- **Cloudflare account:** enable **2FA** (passkey or authenticator app).
- **Google account** (Gmail + Voice + Calendar): turn on **2-Step Verification** and add a **passkey**. This account is the master key — give it the strongest lock.
- **Mobile carrier:** add a **SIM-swap / port-out PIN** by phone or app.
- Prefer passkeys/authenticator over SMS codes (SMS is SIM-swap-vulnerable).

---

## 14. Get found — Google Business Profile

**`[BROWSER]`** Create/claim at **google.com/business**. Use the **exact** name, phone (the Voice number), and service area that the site uses (the page already carries matching `LocalBusiness` data). In a small town, a few 5-star reviews make her the obvious choice.

---

## 15. Secrets checklist (all of them)

| Secret | Where | Command |
|---|---|---|
| Turnstile secret | Worker | `npx wrangler secret put TURNSTILE_SECRET` |
| Admin key (optional) | Worker | `npx wrangler secret put ADMIN_KEY` |
| Turnstile **site** key | `public/index.html` | edit `var TURNSTILE_SITEKEY='...'` |
| Cloudflare login | local | `npx wrangler login` |

Nothing else. No API keys in any file.

---

## 16. Final test checklist

- [ ] Site loads at the custom domain on a real phone.
- [ ] **Call** and **Text** open the dialer/Messages to the Voice number, text pre-filled.
- [ ] Submit a test request → Mariah's Gmail gets the "New request" email within seconds, with the **➕ Add to my calendar** button + `appointment.ics`.
- [ ] Tap the green calendar button → Google Calendar opens pre-filled → Save.
- [ ] With Turnstile on, the check appears above **Send**; a bot/empty token is rejected.
- [ ] `/api/leads?key=...` shows the test row with a ✓ under **Emailed**.
- [ ] Send a test from an outside address → it lands in inbox (check spam once, mark "not spam").
- [ ] DMARC report email arrives at the `rua` address within a day or two.

When all boxes are checked, it's airtight: bots stopped, no lead lost, mail authenticated, accounts locked, and the call/text lifeline works no matter what.

---

## 17. How Mariah uses it (zero learning curve)

A request arrives as a Gmail notification (or, more often, a **text** straight to her Voice number). She reads it, calls or texts to confirm and agree a price, taps **Add to my calendar** → Save, and hits **Reply** to reach the customer. No dashboard, no login, no monthly bill.

---

## 18. Optional future upgrades (all free; not needed to be "done")

- **Customer auto-reply** ("got your request, I'll be in touch") via Brevo's free 300/day — needs a Brevo key.
- **Stale-lead nudge:** an hourly Cron that texts/emails Mariah if a saved lead is unanswered >3h (the D1 table already supports it).
- **Kill the last canvas:** convert the hero's seasonal scene from `<canvas>` to SVG. It already has a graceful gradient fallback, so this is hardening, not a fix.
- **Reminder SMS** to customers (Telnyx + 10DLC, ~$1–3/mo) — the only thing that ever costs money, and only if she wants it.

---

## 19. Cost ledger

| | Cost |
|---|---|
| Domain | ~$10–11 / year |
| Cloudflare Workers Paid | $5 / month (already have it) |
| Hosting, email, form, D1, Turnstile, Voice, Calendar, analytics | $0 |
| **Total** | **~$5.83 / month** |

That's the whole bill. Everything else is free-tier and well within limits for a solo seasonal business.
