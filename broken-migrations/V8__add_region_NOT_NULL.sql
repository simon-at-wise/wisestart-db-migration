-- BROKEN: Trying to add NOT NULL constraint when existing data has NULLs
-- This will fail because players table already has rows with NULL region

ALTER TABLE players
ADD COLUMN region VARCHAR(50) NOT NULL DEFAULT 'UNKNOWN';
