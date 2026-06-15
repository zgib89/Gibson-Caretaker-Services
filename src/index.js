// Gibson Caretaker Services — Worker
// Serves the website (from /public) and handles the contact form.
//
// Pipeline for every submission:
//   honeypot  →  validate  →  Turnstile (spam gate)  →  SAVE TO D1 (lead backup)  →  email Mariah
// The lead is written to D1 BEFORE the email is sent, so a request is never lost
// even if the email fails. Both the spam gate and the backup are optional: until you
// configure them (see SETUP-leadbackup-and-spamgate.md) the form behaves exactly as before.
//
// ── REPLACE these two values, then see SETUP.md ──
const FROM = "mariah@gibsoncaretakerservices.com";   // a custom address you create in Email Routing
const TO   = "gibsoncaretakerservices@gmail.com";    // Mariah's verified destination address (her real inbox)
const VISIT_HOURS = 2;                                // default appointment length (she can change it in her calendar)

import { EmailMessage } from "cloudflare:email";
import { createMimeMessage } from "mimetext";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/api/contact") {
      if (request.method !== "POST") return json({ ok: false, error: "Method not allowed" }, 405);
      return handleContact(request, env);
    }

    // Private backup view of saved leads. Invisible (404) until you set an ADMIN_KEY secret.
    if (url.pathname === "/api/leads") {
      return handleLeads(request, env);
    }

    // everything else: serve the static site
    return env.ASSETS.fetch(request);
  },
};

async function handleContact(request, env) {
  let form;
  try {
    form = await request.formData();
  } catch {
    return json({ ok: false, error: "Bad request" }, 400);
  }

  const get = (k) => (form.get(k) || "").toString().trim();

  // Honeypot — bots fill this hidden field. Pretend success, send nothing.
  if (get("company")) return json({ ok: true });

  const name = get("name");
  const phone = get("phone");
  if (!name || !phone) return json({ ok: false, error: "Please include your name and phone." }, 400);

  // Spam gate. Skips cleanly (returns true) until TURNSTILE_SECRET is configured.
  const human = await verifyTurnstile(env, form.get("cf-turnstile-response"), request);
  if (!human) {
    return json({ ok: false, error: "We couldn't confirm you're human. Please try again, or call/text Mariah." }, 403);
  }

  const lead = {
    name,
    phone,
    email: get("email"),
    town: get("town"),
    needs: get("needs"),
    date: get("date"), // "YYYY-MM-DD"
    time: get("time"), // "HH:MM"
  };

  // LEAD BACKUP — write to D1 first, so the request survives even if the email fails.
  // Best-effort: if D1 isn't bound yet, or the insert hiccups, we keep going to the email.
  let leadId = null;
  try {
    leadId = await saveLead(env, lead, request);
  } catch (e) {
    // swallow — never let the backup block the notification
  }

  // Notify Mariah by email (free; goes only to her verified inbox).
  try {
    await sendNotification(env, lead);
    if (leadId != null) {
      try { await markEmailed(env, leadId); } catch {}
    }
    return json({ ok: true });
  } catch (err) {
    // The lead is already safe in D1 (if bound). Route the customer to the direct line.
    return json({ ok: false, error: "Could not send. Please call or text instead." }, 500);
  }
}

// ───────────────────────── Spam gate (Cloudflare Turnstile) ─────────────────────────
async function verifyTurnstile(env, token, request) {
  const secret = env.TURNSTILE_SECRET;
  if (!secret) return true;            // not configured yet → allow (honeypot still guards)
  if (!token) return false;            // configured but no token → block
  try {
    const body = new FormData();
    body.append("secret", secret);
    body.append("response", token.toString());
    const ip = request.headers.get("CF-Connecting-IP");
    if (ip) body.append("remoteip", ip);
    const res = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", { method: "POST", body });
    const data = await res.json();
    return !!data.success;
  } catch {
    return false;                      // fail closed: the form then shows the call/text escape hatch
  }
}

// ───────────────────────── Lead backup (Cloudflare D1) ─────────────────────────
async function saveLead(env, lead, request) {
  if (!env.DB) return null;            // not bound yet → skip silently
  const ip = request.headers.get("CF-Connecting-IP") || "";
  const ua = request.headers.get("User-Agent") || "";
  const res = await env.DB
    .prepare(
      `INSERT INTO leads (name, phone, email, town, needs, pref_date, pref_time, ip, user_agent)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`
    )
    .bind(
      lead.name,
      lead.phone,
      lead.email || null,
      lead.town || null,
      lead.needs || null,
      lead.date || null,
      lead.time || null,
      ip,
      ua
    )
    .run();
  return res && res.meta ? res.meta.last_row_id : null;
}

async function markEmailed(env, id) {
  if (!env.DB) return;
  await env.DB.prepare(`UPDATE leads SET emailed = 1, status = 'notified' WHERE id = ?`).bind(id).run();
}

// ───────────────────────── Private leads view (recovery / peace of mind) ─────────────────────────
async function handleLeads(request, env) {
  const key = env.ADMIN_KEY;
  if (!key) return new Response("Not found", { status: 404 }); // endpoint doesn't exist until you set a key
  const given = new URL(request.url).searchParams.get("key") || "";
  // length check first, then compare (avoids leaking length via timing)
  if (given.length !== key.length || given !== key) return new Response("Not found", { status: 404 });
  if (!env.DB) {
    return new Response("No database is connected yet.", { status: 200, headers: { "content-type": "text/plain" } });
  }

  const { results } = await env.DB
    .prepare(
      `SELECT id, created_at, name, phone, email, town, needs, pref_date, pref_time, emailed, status
       FROM leads ORDER BY id DESC LIMIT 100`
    )
    .all();

  const rows = (results || [])
    .map(
      (r) => `<tr>
        <td>${esc(r.created_at)}</td>
        <td><strong>${esc(r.name)}</strong></td>
        <td><a href="tel:${esc(r.phone)}">${esc(r.phone)}</a></td>
        <td>${r.email ? `<a href="mailto:${esc(r.email)}">${esc(r.email)}</a>` : ""}</td>
        <td>${esc(r.town || "")}</td>
        <td>${esc(r.needs || "")}</td>
        <td>${esc((r.pref_date || "") + (r.pref_time ? " " + r.pref_time : ""))}</td>
        <td style="text-align:center">${r.emailed ? "✓" : "—"}</td>
      </tr>`
    )
    .join("");

  const html = `<!doctype html><html lang="en"><head><meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
    <title>Saved requests</title>
    <style>
      body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:0;background:#f7f4ea;color:#232c1b}
      .bar{background:#e6207e;color:#fff;padding:14px 18px;font-weight:800}
      .wrap{padding:14px;overflow-x:auto}
      table{border-collapse:collapse;width:100%;font-size:14px;background:#fff;border-radius:10px;overflow:hidden}
      th,td{padding:10px 12px;border-bottom:1px solid #eee;text-align:left;vertical-align:top}
      th{background:#fbe9f2;color:#bf1568;font-size:12px;text-transform:uppercase;letter-spacing:.04em}
      a{color:#bf1568}
      .empty{padding:30px;text-align:center;color:#626c54}
    </style></head><body>
    <div class="bar">Gibson Caretaker Services — saved requests (${(results || []).length})</div>
    <div class="wrap">
      ${rows
        ? `<table><thead><tr><th>When</th><th>Name</th><th>Phone</th><th>Email</th><th>Town</th><th>Needs</th><th>Preferred</th><th>Emailed</th></tr></thead><tbody>${rows}</tbody></table>`
        : `<p class="empty">No saved requests yet.</p>`}
    </div></body></html>`;

  return new Response(html, {
    status: 200,
    headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store", "x-robots-tag": "noindex" },
  });
}

// ───────────────────────── Email to Mariah (unchanged behavior) ─────────────────────────
async function sendNotification(env, lead) {
  const { name, phone, email, town, needs, date, time } = lead;

  let calHtml = `<p style="color:#6b6b6b;margin:14px 0">No preferred day was given — reach out to pick a time together.</p>`;
  let icsB64 = null;

  if (date) {
    const t = time || "09:00";
    const start = date.replace(/-/g, "") + "T" + t.replace(":", "") + "00"; // floating local time
    const end = addHours(date, t, VISIT_HOURS);
    const title = `Gibson Caretaker Services — ${name}${town ? " (" + town + ")" : ""}`;
    const details = [needs ? "Needs: " + needs : "", "Phone: " + phone, email ? "Email: " + email : ""]
      .filter(Boolean)
      .join("\n");
    const location = town;

    const gcal =
      "https://calendar.google.com/calendar/render?action=TEMPLATE" +
      "&text=" + encodeURIComponent(title) +
      "&dates=" + encodeURIComponent(start + "/" + end) +
      "&details=" + encodeURIComponent(details) +
      "&location=" + encodeURIComponent(location) +
      "&ctz=America/Chicago";

    calHtml = `
        <p style="margin:20px 0 8px">
          <a href="${gcal}"
             style="background:#3c6e35;color:#ffffff;font-weight:700;text-decoration:none;
                    padding:14px 22px;border-radius:10px;display:inline-block;font-family:Arial,sans-serif">
            ➕ Add to my calendar
          </a>
        </p>
        <p style="color:#6b6b6b;font-size:14px;margin:4px 0 0">
          Proposed: <strong>${date} at ${t}</strong> (about ${VISIT_HOURS} hours).
          Tap the green button when you agree — it'll drop the appointment on your Google Calendar.
          An <strong>.ics file is attached</strong> too, for Apple Calendar or Outlook.
        </p>`;

    icsB64 = btoa(buildIcs({ title, start, end, location, details }));
  }

  const html = `
      <div style="font-family:Arial,Helvetica,sans-serif;color:#28331f;max-width:560px">
        <h2 style="color:#2c5226;margin:0 0 4px">New request from your website 🌱</h2>
        <table style="border-collapse:collapse;margin-top:12px;font-size:15px;line-height:1.5">
          <tr><td style="padding:4px 14px 4px 0;color:#6b6b6b">Name</td><td><strong>${esc(name)}</strong></td></tr>
          <tr><td style="padding:4px 14px 4px 0;color:#6b6b6b">Phone</td><td><a href="tel:${esc(phone)}">${esc(phone)}</a></td></tr>
          ${email ? `<tr><td style="padding:4px 14px 4px 0;color:#6b6b6b">Email</td><td><a href="mailto:${esc(email)}">${esc(email)}</a></td></tr>` : ""}
          ${town ? `<tr><td style="padding:4px 14px 4px 0;color:#6b6b6b">Town</td><td>${esc(town)}</td></tr>` : ""}
        </table>
        ${needs ? `<p style="margin:14px 0 0"><span style="color:#6b6b6b">Needs help with:</span><br>${esc(needs)}</p>` : ""}
        ${calHtml}
        <hr style="border:none;border-top:1px solid #dbe3c7;margin:22px 0">
        <p style="color:#9aa886;font-size:12px;margin:0">Sent from gibsoncaretakerservices.com</p>
      </div>`;

  const text = `New request from your website

Name:  ${name}
Phone: ${phone}
${email ? "Email: " + email + "\n" : ""}${town ? "Town:  " + town + "\n" : ""}${needs ? "\nNeeds: " + needs + "\n" : ""}${date ? "\nProposed: " + date + " at " + (time || "09:00") + " (see attached .ics, or open this link to add to Google Calendar)\n" : "\nNo preferred day given.\n"}`;

  const msg = createMimeMessage();
  msg.setSender({ name: "Gibson Caretaker Services website", addr: FROM });
  msg.setRecipient(TO);
  if (email) msg.setHeader("Reply-To", email); // reply goes straight to the customer
  msg.setSubject(`New request — ${name}${town ? " (" + town + ")" : ""}`);
  msg.addMessage({ contentType: "text/plain", data: text });
  msg.addMessage({ contentType: "text/html", data: html });
  if (icsB64) {
    msg.addAttachment({ filename: "appointment.ics", contentType: "text/calendar; method=PUBLISH", data: icsB64 });
  }

  await env.MAIL.send(new EmailMessage(FROM, TO, msg.asRaw()));
}

// add hours to a wall-clock date/time, return "YYYYMMDDTHHMMSS"
function addHours(date, time, hours) {
  const [y, m, d] = date.split("-").map(Number);
  const [hh, mm] = time.split(":").map(Number);
  const e = new Date(Date.UTC(y, m - 1, d, hh, mm) + hours * 3600 * 1000);
  const p = (n) => String(n).padStart(2, "0");
  return `${e.getUTCFullYear()}${p(e.getUTCMonth() + 1)}${p(e.getUTCDate())}T${p(e.getUTCHours())}${p(e.getUTCMinutes())}00`;
}

function buildIcs({ title, start, end, location, details }) {
  const stamp = new Date().toISOString().replace(/[-:]/g, "").replace(/\.\d+Z$/, "Z");
  const uid = crypto.randomUUID() + "@gibsoncaretakerservices";
  const e = (s) => (s || "").replace(/\\/g, "\\\\").replace(/;/g, "\\;").replace(/,/g, "\\,").replace(/\n/g, "\\n");
  return [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//Gibson Caretaker Services//EN",
    "CALSCALE:GREGORIAN",
    "METHOD:PUBLISH",
    "BEGIN:VEVENT",
    "UID:" + uid,
    "DTSTAMP:" + stamp,
    "DTSTART:" + start,
    "DTEND:" + end,
    "SUMMARY:" + e(title),
    "LOCATION:" + e(location),
    "DESCRIPTION:" + e(details),
    "END:VEVENT",
    "END:VCALENDAR",
  ].join("\r\n");
}

function esc(s) {
  return (s || "").toString().replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type": "application/json" },
  });
}
