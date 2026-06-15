# Gibson Caretaker Services — Setup Guide

Everything here is **free except the domain** (~$10–11/year). No subscriptions. Plan on about an hour the first time.

You'll set up four things, in order:
1. The domain (Cloudflare Registrar)
2. Branded email + the inbox the form sends to (Cloudflare Email Routing)
3. The website + form handler (one Cloudflare Worker)
4. Point the domain at the site, then test

---

## Before you start
- A **free Cloudflare account** → https://dash.cloudflare.com/sign-up
- **Node.js** installed on your computer → https://nodejs.org (the "LTS" version)
- Mariah's existing **email inbox** (e.g. her Gmail) — this is where requests will land

---

## Step 1 — Register the domain
1. In the Cloudflare dashboard, go to **Domain Registration → Register Domains**.
2. Search for the name (e.g. `gibsoncaretakerservices.com`). A `.com` is about **$10.44/year, same price at renewal**, with free privacy.
3. Buy it. It's instant, and the domain is automatically managed by Cloudflare's DNS (exactly what we want).

> You've already registered **gibsoncaretakerservices.com** on Cloudflare — so you can skip ahead. Just confirm it shows up under **Domain Registration** in your dashboard before moving on.

---

## Step 2 — Set up email (this powers the inbox AND the contact form)
In the dashboard, open your domain and go to **Email → Email Routing**, then **Get started**.

**a) Add the destination (where mail lands):**
- Under **Destination addresses**, add Mariah's real inbox (e.g. `gibsoncaretakerservices@gmail.com`).
- Cloudflare emails her a verification link — **she must click it.** Nothing works until this address shows **Verified**.

**b) Create the branded address:**
- Under **Routing rules → Custom addresses**, create `mariah@gibsoncaretakerservices.com` → forward to her verified inbox.
- (Optional but handy) turn on **Catch-all** → her inbox, so anything `@gibsoncaretakerservices.com` reaches her.
- Cloudflare adds the needed DNS records for you automatically. Approve them if asked.

Now `mariah@gibsoncaretakerservices.com` is a real, free, professional address that forwards to her normal inbox. ✅

---

## Step 3 — Put your details into the files
You downloaded a folder called `gibson-caretaker-services`. Edit these three files:

**Phone number** — the site ships with a placeholder, `(608) 555-5555`. Set the real
number with one command from the project folder (updates every call link, text link,
on-screen number, and the SEO data at once):

```
node scripts/set-phone.mjs 6085551234
```

(Optional) update the footer email if your domain isn't `gibsoncaretakerservices.com`.

**`wrangler.jsonc`** — replace:
- `gibsoncaretakerservices@gmail.com` → her verified inbox from Step 2a

**`src/index.js`** — replace at the top:
- `TO`   → her verified inbox (same as above)
- `FROM` → `mariah@gibsoncaretakerservices.com` (or your branded address, if the domain differs)

> `FROM` must be the custom address you made in Step 2b, and `TO` must be the verified destination. That pairing is what makes sending **free**.

---

## Step 4 — Deploy the site
Open a terminal **inside the `gibson-caretaker-services` folder** and run:

```bash
npm install
npx wrangler login        # opens your browser to authorize (one time)
npx wrangler deploy
```

That publishes the site to a temporary `*.workers.dev` URL — open it to confirm it loads.

---

## Step 5 — Point the domain at the site
1. Dashboard → **Workers & Pages → `gibson-caretaker-services` → Settings → Domains & Routes**.
2. **Add → Custom domain** → `gibsoncaretakerservices.com`. Add `www.gibsoncaretakerservices.com` too.
3. Wait a few minutes for it to go live (it's automatic since the domain is on Cloudflare).

---

## Step 6 — Test it
1. Visit `https://gibsoncaretakerservices.com` on your phone.
2. Tap **Call** and **Text** — they should open your phone to her number.
3. Fill in the form, pick a **preferred day and time**, and submit.
4. Check Mariah's inbox: a "New request" email should arrive within seconds, with an **"➕ Add to my calendar"** button and an `appointment.ics` attachment.
5. Tap the green button → it opens Google Calendar pre-filled → **Save**. That's the whole "she agrees → it's on her calendar" flow. 🎉

> First send is slow to arrive? Check the spam folder once and mark "not spam." Future ones go to the inbox.

---

## How Mariah uses it day to day (about 30 seconds)
1. A request email arrives on her phone (Gmail app notification).
2. She reads what they need, calls or texts to confirm, picks a time.
3. When she agrees, she taps **Add to my calendar** → Save. Done.
4. If the customer left an email, she can just hit **Reply** and it goes straight to them.

No logins to learn, no dashboard, no monthly bill.

---

## Nice extras (optional, all free)
- **Google Business Profile** (google.com/business): do this early — it's how people find her on Google Maps and search, and where reviews live. In a small town, a few 5-star reviews make her the obvious choice.
- **Reply *from* the branded address:** in Gmail → Settings → Accounts → "Send mail as," she can add `mariah@gibsoncaretakerservices.com`. (Replying from plain Gmail is totally fine too — the branded address still works for *receiving*.)
- **Add more towns or services:** just edit `public/index.html` and run `npx wrangler deploy` again.

---

## What it costs
| | Cost |
|---|---|
| Domain | ~$10–11 / year |
| Website hosting (Worker) | $0 |
| Branded email (Email Routing) | $0 |
| Contact-form emails to her | $0 |
| Calendar feature | $0 |
| **Total ongoing** | **~$10–11 / year** |

That's it. One small yearly domain bill, nothing else.
