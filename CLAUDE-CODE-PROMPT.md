# Prompt for Claude Code — Deploy Gibson Caretaker Services

> Paste everything below the line into Claude Code, with this project folder open.

---

You're deploying a **finished** web project for a real small business: **Gibson Caretaker Services**, a one-person seasonal yard, garden, and home-help service in Darlington, Wisconsin, run by Mariah Gibson. The complete, validated source is in this folder.

**Your mission:** take it from this repository to **fully live, tested, and airtight** — and do as much as humanly *and inhumanly* possible yourself.

## Start here
Read **`HANDOFF.md`** end to end. It is the complete 19-step deployment guide: every command, every value, the exact DNS records, the security steps, and a final test checklist. Then skim `README.md`, `SETUP.md`, `SETUP-leadbackup-and-spamgate.md`, and `src/index.js` so you understand the architecture. `THE-ENDGAME-flow-and-reliability.md` explains the design intent — honor it. All the reference values (domain, emails, `FROM`/`TO`, bindings, secrets) are in `HANDOFF.md` §1.

## The challenge — be relentless and resourceful
Treat every step I labeled **`[BROWSER]`** ("a human must do this in a dashboard") as a **hypothesis to disprove, not a wall to stop at.** Before you hand *any* step back to the human, exhaust your options:

- Use the **wrangler CLI** for everything it can do: `deploy`, `d1 create` / `execute`, `secret put`, custom domains, `tail`/logs.
- Use the **Cloudflare API** (ask the human for a scoped API token, or reuse wrangler's auth) to do the `[BROWSER]` steps that actually have API equivalents — for example:
  - add the **DMARC** DNS record (and verify SPF/DKIM exist),
  - create and configure **Email Routing** addresses and rules,
  - **create the Turnstile widget and read back its site + secret keys** programmatically,
  - attach the **custom domain** / routes to the Worker.
- **Discover and use every tool, MCP server, connector, and skill available to you** in this environment — a Cloudflare connector, a Git host connector, a browser tool, anything. If a connector can do a step, use it. If a CLI flag or API endpoint exists, prefer it over asking a human.
- If your first approach is blocked, **find another path.** Pull up the Cloudflare API reference or wrangler docs, adapt, and push through. Don't give up after one error — diagnose and route around it.

The bar: **the human should have to do as little as possible.** Hand back only what genuinely requires *their* identity, *their* click, or *their* money.

## What truly only the human can do (escalate these clearly — don't burn time fighting them)
- Anything inside the **Google account**: clicking Cloudflare's verification link sent to the Gmail destination; creating the **Google Voice** number; enabling 2-Step Verification / passkeys; claiming the **Google Business Profile**.
- **Account-security** actions: Cloudflare and Google 2FA/passkeys, and the carrier **SIM-swap PIN**.
- Anything needing a **password, a payment, or human identity verification.**

For each of these, give the human an **exact, copy-paste-ready instruction with the direct link** — and keep working on everything else in the meantime. Never block your whole run on a human step you could sequence around.

## Non-negotiable guardrails
- **Never** print, paste, log, or commit any secret, API token, or password. Use `wrangler secret put` and environment variables. Confirm `.gitignore` covers `.dev.vars` / `.env`. The repo must stay free of secrets **and** of the owner's real phone number.
- **Do not put a non-working number in front of real customers.** The site ships with a placeholder, `(608) 555-5555`. Get the real **Google Voice** number first, then run `node scripts/set-phone.mjs <number>`. You may deploy and test on the `*.workers.dev` URL with the placeholder, but **do not attach/announce the public domain for customer use until the real number is in.**
- **Verify as you go.** Never assume a step worked — check it (curl the endpoint, query D1, read the deploy output, send a test).

## Definition of done
1. Site **live** on the custom domain — or, if a human-only step blocks the domain, live on `*.workers.dev` with a crisp list of exactly what remains.
2. Contact form **emails Mariah**, **saves to D1**, and is **protected by Turnstile**.
3. **SPF + DKIM** present (auto via Email Routing) and **DMARC** added.
4. **Every box in `HANDOFF.md` §16 (the test checklist) actually run and checked** — not assumed.
5. A **final report**: what you did, proof it works (your test results), and a short numbered list of the exact human-only actions still required, each with a link.

Work autonomously. Don't stop at the first obstacle — route around it. Use every tool you have. Show Mariah what a finished, professional, bulletproof launch looks like. **Go.**
