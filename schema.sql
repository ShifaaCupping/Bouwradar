-- Nieuwe database: plak dit in de D1-console.
CREATE TABLE IF NOT EXISTS subscribers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL UNIQUE,
  sets TEXT NOT NULL DEFAULT '[]',
  token TEXT,
  consent_at TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_subscribers_token ON subscribers(token);
