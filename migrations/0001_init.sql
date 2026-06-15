-- Gibson Caretaker Services — lead backup table
-- Apply with:  npx wrangler d1 execute gibson-leads --remote --file=migrations/0001_init.sql

CREATE TABLE IF NOT EXISTS leads (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT    NOT NULL DEFAULT (datetime('now')),
  name       TEXT    NOT NULL,
  phone      TEXT    NOT NULL,
  email      TEXT,
  town       TEXT,
  needs      TEXT,
  pref_date  TEXT,
  pref_time  TEXT,
  status     TEXT    NOT NULL DEFAULT 'new',   -- new | notified
  emailed    INTEGER NOT NULL DEFAULT 0,       -- 0 = email not yet confirmed sent, 1 = sent
  ip         TEXT,
  user_agent TEXT,
  source     TEXT    DEFAULT 'website'
);

CREATE INDEX IF NOT EXISTS idx_leads_created ON leads (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_leads_status  ON leads (status);
