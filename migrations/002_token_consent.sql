-- Alleen nodig als je de tabel al had aangemaakt met de eerste versie van schema.sql.
ALTER TABLE subscribers ADD COLUMN token TEXT;
ALTER TABLE subscribers ADD COLUMN consent_at TEXT;
CREATE UNIQUE INDEX IF NOT EXISTS idx_subscribers_token ON subscribers(token);
