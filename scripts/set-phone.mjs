#!/usr/bin/env node
/*
 * set-phone.mjs — swap the business phone number across the whole site in one command.
 *
 *   node scripts/set-phone.mjs 6085551234      # 10-digit US number
 *
 * It rewrites every form the number appears in (tel: links, pre-filled sms: links,
 * the on-screen (xxx) xxx-xxxx text, and the +1-xxx-xxx-xxxx in the SEO schema),
 * leaving the pre-filled text message body untouched. Run wrangler deploy after.
 */
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const digits = (process.argv[2] || '').replace(/\D/g, '');
if (digits.length !== 10) {
  console.error('Usage: node scripts/set-phone.mjs 6085551234  (exactly 10 digits)');
  process.exit(1);
}
const a = digits.slice(0, 3), b = digits.slice(3, 6), c = digits.slice(6);
const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const files = ['public/index.html'];

const countRe = /(tel:\+1\d{10}|sms:\+1\d{10}|\+1-\d{3}-\d{3}-\d{4}|\(\d{3}\)(?:&nbsp;|\s)?\d{3}-\d{4})/g;
let grand = 0;
for (const rel of files) {
  const p = join(root, rel);
  const before = readFileSync(p, 'utf8');
  const n = (before.match(countRe) || []).length;
  let s = before
    .replace(/tel:\+1\d{10}/g, `tel:+1${digits}`)
    .replace(/sms:\+1\d{10}/g, `sms:+1${digits}`)
    .replace(/\+1-\d{3}-\d{3}-\d{4}/g, `+1-${a}-${b}-${c}`)
    .replace(/\((\d{3})\)((?:&nbsp;|\s)?)\d{3}-\d{4}/g, `(${a})$2${b}-${c}`);
  if (s !== before) writeFileSync(p, s);
  grand += n;
  console.log(`${rel}: ${n} phone references updated`);
}
console.log(`\nBusiness number is now (${a}) ${b}-${c}  (${grand} references total).`);
console.log('Next:  npx wrangler deploy');
