# Database Migration Exercises - Solutions Guide (INSTRUCTORS ONLY)

This guide contains complete solutions and teaching notes for all exercises. Extract this file before giving the repository to students.

---

## Exercise 0: Setup

### Expected Outcome
- Application starts successfully
- Students can query endpoints and see 10 players, 20 matches
- Students explore `flyway_schema_history` table

### Common Mistakes
- Docker not running
- Port 3306 already in use
- Not waiting for database to be ready

### Discussion Points
- Flyway tracks: version, description, script name, checksum, execution time, success/failure
- Checksum validates that applied migrations haven't been modified
- `installed_rank` shows the order migrations were applied

### Time Estimate
5 minutes

---

## Exercise 1: Backfill Historical Data

### Expected Outcome
Students create a working V3 migration using LOAD DATA LOCAL INFILE or batched INSERTs to load 100k+ rows.

### Common Mistakes
- File path issues with LOAD DATA LOCAL INFILE
- Not enabling `local_infile=1` (already set in docker-compose)
- Trying to load absolute paths instead of relative
- Timeout on default Flyway settings

### Solution (Option A: LOAD DATA LOCAL INFILE)

Create `src/main/resources/db/migration/V3__Load_historical_data.sql`:

```sql
-- Load historical players
LOAD DATA LOCAL INFILE '../../data/players_historical.csv'
INTO TABLE players
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(username, email, @created_at)
SET created_at = STR_TO_DATE(@created_at, '%Y-%m-%d %H:%i:%s');

-- Load historical matches
LOAD DATA LOCAL INFILE '../../data/matches_historical.csv'
INTO TABLE matches
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(player_id, score, @played_at)
SET played_at = STR_TO_DATE(@played_at, '%Y-%m-%d %H:%i:%s');
```

**Note:** File paths may need adjustment depending on where Flyway runs from.

### Solution (Option B: Using Docker volume mount)

Better approach - mount the data directory in docker-compose.yml and use absolute path:

```yaml
services:
  mariadb:
    volumes:
      - ./data:/data
```

Then:
```sql
LOAD DATA LOCAL INFILE '/data/players_historical.csv' ...
```

### Timeout Configuration

If migration times out, adjust in `application.yml`:

```yaml
spring:
  flyway:
    placeholders:
      flyway.commandLineArgs: "-X -commandLineArgs=-Dflyway.timeout=600"
```

Or run with increased timeout:
```bash
./gradlew bootRun -Dflyway.timeout=600
```

### Discussion Points
- LOAD DATA INFILE is much faster than batched INSERTs for large datasets
- Timeout defaults are 60 seconds - may need adjustment for large migrations
- Local file loading requires `local_infile=1` setting
- In production, consider using Flyway Java migrations for complex data loads
- Transaction boundaries: LOAD DATA is not transactional, partial loads can occur on failure

### Time Estimate
15-20 minutes

---

## Exercise 2: Adding Safe Columns

### Expected Outcome
Students successfully add nullable columns without any issues.

### Solution

Create `src/main/resources/db/migration/V4__Add_country_to_players.sql`:

```sql
ALTER TABLE players ADD COLUMN country VARCHAR(2) NULL;
```

Create `src/main/resources/db/migration/V5__Add_game_mode_to_matches.sql`:

```sql
ALTER TABLE matches ADD COLUMN game_mode VARCHAR(20) NULL;
```

### Explanation
Adding nullable columns is safe because:
- Existing rows get NULL value automatically
- No data backfill required
- No table rewrite in most cases (metadata-only change)
- Does not block writes

### Discussion Points
- NULL is the default value for new columns
- This is a non-blocking operation
- If you need NOT NULL, do it in multiple steps
- Consider setting a DEFAULT value: `ADD COLUMN country VARCHAR(2) NULL DEFAULT 'US'`

### Time Estimate
5 minutes

---

## Exercise 3: Adding Indexes - Table Locking

### Expected Outcome
Students add an index and observe it takes several seconds with 500k rows. They experience table locking.

### Solution

Create `src/main/resources/db/migration/V6__Add_score_index.sql`:

```sql
CREATE INDEX idx_matches_score ON matches(score);
```

Or with explicit algorithm:
```sql
CREATE INDEX idx_matches_score ON matches(score) ALGORITHM=INPLACE, LOCK=NONE;
```

### Execution Time
With 500k rows: typically 5-15 seconds depending on hardware.

### Explanation
- Index creation on large tables takes time
- In MySQL 5.6+, ALGORITHM=INPLACE allows concurrent reads but may still block writes
- ALGORITHM=COPY rebuilds the entire table (very slow, full lock)
- MySQL defaults to INPLACE when possible

### Discussion Points
- Always estimate execution time before running migrations in production
- Use `EXPLAIN` to verify the index is being used
- Consider online schema change tools for very large tables (pt-online-schema-change)
- Monitor table locks: `SHOW PROCESSLIST;` or `SHOW OPEN TABLES WHERE In_use > 0;`

### Testing Index Usage
```sql
EXPLAIN SELECT * FROM matches WHERE score > 3000 ORDER BY score DESC LIMIT 10;
```
Should show "Using index" in Extra column.

### Time Estimate
10 minutes

---

## Exercise 4: Checksum Mismatch Recovery

### Expected Outcome
Students see Flyway reject startup due to checksum mismatch, then use `flyway repair` to fix it.

### What Happens
After editing V2 and restarting:
```
Validate failed: Migration checksum mismatch for migration version 2
```

### Solution

**Step 1: Understand the problem**
```bash
./gradlew flywayInfo
```
Shows checksum mismatch for V2.

**Step 2: Undo the edit (revert V2 to original)**

**Step 3: Repair Flyway history**
```bash
./gradlew flywayRepair
```

**Step 4: Restart application**
```bash
./gradlew bootRun
```

### Alternative: Keep the Edit
If the edit is intentional (rare), you can:
```bash
./gradlew flywayRepair
```
This updates the checksum in `flyway_schema_history` to match the modified file.

### Explanation
- Flyway calculates a checksum (hash) of each migration file when applied
- On startup, it recalculates and compares checksums
- Mismatch = file was modified after being applied (potential data inconsistency)
- `flyway repair` recalculates checksums and updates the history table

### Discussion Points
- **NEVER edit applied migrations in production**
- Proper fix: create a NEW migration (V3, V4, etc.) to make changes
- Editing is only safe if migration hasn't been applied to other environments
- Version control helps prevent this - migration files should be immutable

### Time Estimate
10 minutes

---

## Exercise 5: Failed Migration Recovery

### Expected Outcome
Students identify that V6 failed midway, fix the SQL syntax error, use `flyway repair`, and re-run successfully.

### What Happens
After copying the broken V6 and starting the app:
```
Migration V6__add_achievements.sql failed
SQL State: 42000
Error Code: 1064
Message: You have an error in your SQL syntax near '100)' at line X
```

Database state:
- `achievements` table EXISTS (created before error)
- `player_achievements` table DOES NOT EXIST (never reached)
- `flyway_schema_history` has V6 marked as `success = 0`

### Solution

**Step 1: Investigate database state**
```sql
SHOW TABLES;  -- achievements exists, player_achievements doesn't
SELECT * FROM flyway_schema_history WHERE version = '6';  -- shows success = false
```

**Step 2: Fix the SQL file**

Edit `src/main/resources/db/migration/V6__add_achievements.sql`:

```sql
-- Fixed version
CREATE TABLE achievements (
    id BIGINT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    points INT NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Fixed: proper closing quote
INSERT INTO achievements (name, description, points) VALUES
('First Win', 'Win your first match', 10),
('Winning Streak', 'Win 5 matches in a row', 50),
('High Scorer', 'Score over 5000 points', 100);  -- Fixed here

CREATE TABLE player_achievements (
    player_id BIGINT NOT NULL,
    achievement_id BIGINT NOT NULL,
    earned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (player_id, achievement_id),
    CONSTRAINT fk_player_achievements_player FOREIGN KEY (player_id) REFERENCES players(id),
    CONSTRAINT fk_player_achievements_achievement FOREIGN KEY (achievement_id) REFERENCES achievements(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Step 3: Mark V6 as pending again**
```bash
./gradlew flywayRepair
```

This marks failed migrations as pending so they can be re-run.

**Step 4: Re-run application**
```bash
./gradlew bootRun
```

V6 now runs successfully from the beginning (including re-creating the achievements table with CREATE TABLE IF NOT EXISTS or after manual cleanup).

**Alternative: Manual cleanup before repair**
```sql
DROP TABLE IF EXISTS achievements;
```
Then flywayRepair and restart.

### Explanation
MySQL DDL is **not transactional**:
- CREATE TABLE commits immediately
- Cannot be rolled back
- If migration fails, successfully executed statements remain applied
- This is why migrations should be as atomic as possible

### Discussion Points
- Why isn't DDL transactional in MySQL?
- PostgreSQL has transactional DDL - migrations can be rolled back
- Best practices: Keep migrations small and atomic
- Separate DDL and DML (data changes) into different migrations
- Consider data migrations as separate Java-based Flyway callbacks for complex logic
- In production: test migrations on a copy of production data first

### Time Estimate
15-20 minutes

---

## Exercise 6: Column Type Change - Locking Impact

### Expected Outcome
Students observe that ALTER COLUMN on 500k rows takes noticeable time and locks the table.

### Solution

Create `src/main/resources/db/migration/V7__Change_score_to_bigint.sql`:

```sql
ALTER TABLE matches MODIFY COLUMN score BIGINT NOT NULL;
```

### Execution Time
With 500k rows: typically 10-30 seconds depending on hardware.

### Explanation
- `ALTER TABLE ... MODIFY COLUMN` requires table rebuild in most cases
- Table is locked for writes during the operation
- Reads may be blocked depending on MySQL version and algorithm
- This is a **risky operation** in production on large tables

### Discussion Points
- Always test on production-size data before running in production
- Estimate execution time: roughly proportional to table size
- Alternatives for large tables:
  1. **Expand-contract pattern:**
     - Add new BIGINT column
     - Dual-write to both columns
     - Migrate data in batches
     - Update code to read new column
     - Drop old column
  2. **Online schema change tools:** pt-online-schema-change (Percona Toolkit)
  3. **Blue-green deployment:** Run migration on secondary, switch over
- In modern MySQL, some operations support ALGORITHM=INSTANT (metadata-only)

### Testing Impact
During migration, try:
```sql
INSERT INTO matches (player_id, score) VALUES (1, 9999);
```
Query will wait/block until migration completes.

### Time Estimate
10 minutes

---

## Exercise 7: Adding NOT NULL Without Backfill

### Expected Outcome
Students see the migration fail, understand why, and implement the proper multi-step approach.

### What Happens
After running the broken V8:
```
ERROR 1364 (HY000): Field 'region' doesn't have a default value
```

Database state:
- Migration failed
- Column was NOT added (operation failed before completion)

### Solution (Multi-Step Approach)

**Step 1: Add column as nullable**

Create `src/main/resources/db/migration/V8__Add_region_column_nullable.sql`:

```sql
ALTER TABLE players ADD COLUMN region VARCHAR(50) NULL;
```

**Step 2: Backfill data**

Create `src/main/resources/db/migration/V9__Backfill_region_data.sql`:

```sql
-- Set default region for existing players
UPDATE players SET region = 'US' WHERE region IS NULL;

-- Or more sophisticated logic:
-- UPDATE players SET region = CASE
--   WHEN email LIKE '%@example.com' THEN 'US'
--   WHEN email LIKE '%@gamers.example.com' THEN 'XX'  -- Unknown
--   ELSE 'US'
-- END
-- WHERE region IS NULL;
```

**Step 3: Add NOT NULL constraint**

Create `src/main/resources/db/migration/V10__Make_region_not_null.sql`:

```sql
ALTER TABLE players MODIFY COLUMN region VARCHAR(50) NOT NULL;
```

### Explanation
You cannot add a NOT NULL column to a table with existing data unless:
1. You provide a DEFAULT value, or
2. All existing rows already have non-NULL values

The safe pattern is always:
1. Add nullable
2. Backfill existing data
3. Add NOT NULL constraint

### Alternative: Using DEFAULT

```sql
ALTER TABLE players ADD COLUMN region VARCHAR(50) NOT NULL DEFAULT 'US';
```

This works but may not be semantically correct if 'US' isn't the right default.

### Discussion Points
- Why does MySQL reject NOT NULL on existing data?
- When is it safe to use DEFAULT vs explicit backfill?
- What if backfill is complex (requires joins, external API calls)?
- Consider application-level backfill for complex logic

### Time Estimate
15 minutes

---

## Exercise 8: Renaming Columns - Breaking Changes

### Expected Outcome
Students see that the migration succeeds but the application breaks because the code still references the old column name.

### What Happens
After renaming `username` to `player_name`:
- Migration succeeds
- Application fails with SQL errors:
  ```
  Unknown column 'username' in 'field list'
  ```

### Solution (Quick Fix for Exercise)

**Option A: Revert the migration**

```sql
ALTER TABLE players CHANGE COLUMN player_name username VARCHAR(50) NOT NULL;
```

**Option B: Update the Java code**

Modify `src/main/java/com/wise/leaderboard/model/Player.java`:

```java
@Column(name = "player_name", nullable = false, unique = true, length = 50)
private String username;  // Java field name stays same
```

### Solution (Production-Safe Approach)

Use the **expand-contract pattern** for zero-downtime:

**Phase 1: Expand**
```sql
-- V11: Add new column
ALTER TABLE players ADD COLUMN player_name VARCHAR(50) NULL;

-- V12: Copy data
UPDATE players SET player_name = username;

-- V13: Make new column NOT NULL
ALTER TABLE players MODIFY COLUMN player_name VARCHAR(50) NOT NULL;

-- V14: Add unique constraint
ALTER TABLE players ADD UNIQUE KEY uk_player_name (player_name);
```

**Phase 2: Update code**
- Deploy code that reads/writes both columns

**Phase 3: Contract**
```sql
-- V15: Drop old column
ALTER TABLE players DROP COLUMN username;
```

### Explanation
- Schema changes must be coordinated with code deployments
- Breaking changes cause downtime if not handled carefully
- Expand-contract allows zero-downtime deployments
- Always add new, migrate code, remove old

### Discussion Points
- What other schema changes are "breaking"?
  - Renaming tables
  - Dropping columns
  - Changing column types
  - Removing indexes that code depends on
- How do you handle this in CI/CD pipelines?
- What if you have multiple services depending on the same database?

### Time Estimate
10 minutes

---

## Exercise 9: Duplicate Keys and Idempotency

### Expected Outcome
Students understand idempotency, add proper constraints, and use INSERT IGNORE or ON DUPLICATE KEY UPDATE.

### What Happens (Without Constraints)
- Data loads successfully
- Duplicate records are created
- No error, but data quality issue

### What Happens (With Unique Constraint)
- Duplicate key error
- Migration fails

### Solution Approach

**Step 1: Decide on uniqueness constraint**

Do we want to allow duplicate matches? Probably not if (player_id, played_at) should be unique.

Add constraint in a new migration first:

Create `src/main/resources/db/migration/V10__Add_unique_constraint_matches.sql`:

```sql
-- Add unique constraint on player_id + played_at
-- Assumes each player can only have one match at a specific timestamp
ALTER TABLE matches ADD UNIQUE KEY uk_player_played_at (player_id, played_at);
```

**Step 2: Load data idempotently**

Create `src/main/resources/db/migration/V11__Load_batch2_matches.sql`:

**Option A: INSERT IGNORE (skip duplicates)**
```sql
LOAD DATA LOCAL INFILE '/data/matches_batch2.csv'
IGNORE  -- Skip duplicates
INTO TABLE matches
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(player_id, score, @played_at)
SET played_at = STR_TO_DATE(@played_at, '%Y-%m-%d %H:%i:%s');
```

**Option B: ON DUPLICATE KEY UPDATE (update on conflict)**
Can't use with LOAD DATA directly. Need to load to temp table first:

```sql
-- Create temp table
CREATE TEMPORARY TABLE temp_matches LIKE matches;

-- Load into temp
LOAD DATA LOCAL INFILE '/data/matches_batch2.csv'
INTO TABLE temp_matches
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(player_id, score, @played_at)
SET played_at = STR_TO_DATE(@played_at, '%Y-%m-%d %H:%i:%s');

-- Insert with conflict handling
INSERT INTO matches (player_id, score, played_at)
SELECT player_id, score, played_at FROM temp_matches
ON DUPLICATE KEY UPDATE score = VALUES(score);  -- Update score if duplicate

DROP TEMPORARY TABLE temp_matches;
```

**Option C: Pre-filter duplicates**
```sql
-- Only insert records that don't already exist
INSERT INTO matches (player_id, score, played_at)
SELECT t.player_id, t.score, t.played_at
FROM temp_matches t
LEFT JOIN matches m ON m.player_id = t.player_id AND m.played_at = t.played_at
WHERE m.id IS NULL;
```

### Explanation
- **Idempotency:** Migration can be run multiple times with same result
- **INSERT IGNORE:** Silently skip duplicates (returns warning, not error)
- **ON DUPLICATE KEY UPDATE:** Update existing rows on conflict
- **Pre-filtering:** Explicitly check for existence before inserting

### Which to Use?
- **INSERT IGNORE:** When duplicates should be skipped (most common)
- **ON DUPLICATE KEY UPDATE:** When you want to update existing records
- **Pre-filtering:** When you need explicit control or logging

### Discussion Points
- Why is idempotency important?
  - Migrations may fail midway and need to be re-run
  - Developer may run migration multiple times during testing
  - Production rollback/retry scenarios
- All data migrations should be idempotent when possible
- Test by running migration twice and verifying same result
- Consider logging skipped/updated records for auditing

### Time Estimate
15-20 minutes

---

## Common Questions Across All Exercises

### "Can I just drop and recreate the database?"

Yes! That's what `scripts/reset-database.sh` is for. In these exercises, you have that luxury. In production, you don't.

### "What if I mess up really badly?"

Reset script:
```bash
./scripts/reset-database.sh
rm -rf data/*.csv
./scripts/generate-data.sh
./gradlew clean bootRun
```

### "How do I know if a table is locked?"

```sql
SHOW OPEN TABLES WHERE In_use > 0;
SHOW PROCESSLIST;
```

### "Can I use Flyway undo/rollback?"

Flyway Teams (paid) supports undo migrations. Community edition does not. In practice, most teams write "forward-only" migrations (new migration to fix issues, not rollback).

### "What about transactions?"

- MySQL DDL is not transactional (auto-commit)
- DML (INSERT, UPDATE) can be wrapped in transactions
- Use Java-based migrations for complex transactional logic

### "How do I test migrations before production?"

1. Test locally with production-like data volumes
2. Test on staging environment (copy of production)
3. Estimate execution time
4. Have rollback plan (usually a new migration to undo)
5. Monitor during deployment

---

## Summary: Key Learning Outcomes

By the end of these exercises, students should understand:

1. **Flyway Basics**
   - Versioning and naming conventions
   - Schema history tracking
   - Checksum validation

2. **Safe vs Risky Changes**
   - Adding nullable columns (safe)
   - Adding NOT NULL (risky without backfill)
   - Renaming columns (breaking change)
   - Changing types (locking operation)

3. **Table Locking**
   - Index creation locks tables
   - ALTER operations lock tables
   - Execution time matters
   - ALGORITHM options

4. **Recovery Patterns**
   - Checksum mismatch: flyway repair
   - Failed migrations: fix SQL, repair, re-run
   - Manual database cleanup sometimes needed

5. **Idempotency**
   - Data migrations should be re-runnable
   - INSERT IGNORE vs ON DUPLICATE KEY UPDATE
   - Always test migrations twice

6. **Production Practices**
   - Expand-contract for breaking changes
   - Estimate execution time
   - Test with realistic data volumes
   - Have rollback plans
   - Keep migrations small and focused

---

## Extension Exercises (If Time Permits)

### Exercise 10: Batch Data Updates

Write a migration that updates all matches from 2023 to have `game_mode = 'classic'`.

Learn: Batching updates to avoid long transactions.

### Exercise 11: Complex Foreign Key

Add a `last_match_id` column to players table pointing to their most recent match.

Learn: Handling circular references, nullable foreign keys.

### Exercise 12: Dropping Columns Safely

Remove the `country` column added in Exercise 2 using expand-contract pattern.

Learn: Safe removal of columns in multi-service environments.

---

**End of Solutions Guide**
