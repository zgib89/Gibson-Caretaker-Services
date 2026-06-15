# Turning on the Lead Backup + Spam Gate

Everything is already built into the code. **Until you do the steps below, the site works exactly as it does now** (honeypot-only, email-only). Doing these steps switches on two things:

- **Spam gate (Turnstile):** stops bots from ever reaching the form.
- **Lead backup (D1):** every request is saved to a tiny database *before* the email is sent — so a request is never lost, even if an email hiccups.

You run these once, from the project folder, after `npm install`. Nothing here costs money.

---

## A) Spam gate — Cloudflare Turnstile (free)

1. Cloudflare dashboard → **Turnstile** → **Add widget**.
   - Name: `gibson-form`  ·  Domain: `gibsoncaretakerservices.com`  ·  Mode: **Managed**.
2. Copy the two keys it gives you: a **Site Key** and a **Secret Key**.
3. **Site Key** → open `public/index.html`, find this line near the form script:
   ```js
   var TURNSTILE_SITEKEY='';
   ```
   Paste your site key between the quotes:
   ```js
   var TURNSTILE_SITEKEY='0x4AAAAAAA...yourkey...';
   ```
4. **Secret Key** → run this and paste the secret when prompted:
   ```
   npx wrangler secret put TURNSTILE_SECRET
   ```

> Want to test the wiring first without real keys? Cloudflare's always-pass test pair is
> site key `1x00000000000000000000AA` and secret `1x0000000000000000000000000000000AA`.

---

## B) Lead backup — Cloudflare D1 (free)

1. Create the database:
   ```
   npx wrangler d1 create gibson-leads
   ```
2. It prints a `database_id`. Open `wrangler.jsonc`, find the commented `d1_databases`
   block at the bottom, **uncomment it** (including the leading comma), and paste the id:
   ```jsonc
   ,"d1_databases": [
     { "binding": "DB", "database_name": "gibson-leads", "database_id": "PASTE_IT_HERE" }
   ]
   ```
3. Create the table on the live database:
   ```
   npx wrangler d1 execute gibson-leads --remote --file=migrations/0001_init.sql
   ```

---

## C) (Optional) Private view of saved requests

A backup you can read. Invisible to the world until you set a key.

1. Pick a long random password and set it:
   ```
   npx wrangler secret put ADMIN_KEY
   ```
2. After deploy, view every saved request at:
   ```
   https://gibsoncaretakerservices.com/api/leads?key=YOUR_ADMIN_KEY
   ```
   (Keep that link private — it lists names and phone numbers. Without the key it returns "Not found.")

---

## D) Push it live

```
npx wrangler deploy
```

## E) Confirm it works
- Submit a test request on the site → Mariah's inbox gets the email.
- Open the `/api/leads?key=...` link → the test row is there with a ✓ under **Emailed**.
- Try submitting with the spam gate on → you'll see the Turnstile check appear above the button.

That's it. From here on: nothing lost, bots blocked.
