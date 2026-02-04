# Game Leaderboard Training Project - Design Document

**Date:** 2026-02-04
**Purpose:** Educational project for teaching database migration best practices to new graduates at Wise

## Overview

A Spring Boot application simulating a game leaderboard system, designed to teach database migration best practices through hands-on troubleshooting exercises. Teams of 3-4 graduates will work through increasingly complex migration scenarios, with heavy emphasis on failure recovery.

## Target Audience

Recently graduated software engineers on their first job at Wise, working as fullstack/back-end engineers. They have:
- Mixed database experience levels
- Basic SQL knowledge (SELECT, INSERT, CREATE TABLE)
- Understanding of relational database fundamentals
- Need deeper knowledge of production schema changes, indexes, constraints, and recovery patterns

## Session Format

- **Duration:** 45-60 minutes of hands-on exercises
- **Team size:** 3-4 people per team
- **Structure:** Self-guided with instructors available for questions
- **Documentation style:** Intentionally light to encourage exploration and problem-solving
- **Focus:** Heavy on troubleshooting (60% breaking things and fixing them, 40% successful migrations)

## Tech Stack

- **Framework:** Spring Boot 3.x with Java 21 (matching Wise standards)
- **Database:** MariaDB 11.2 via Docker Compose
- **Migration tool:** Flyway
- **Build system:** Gradle with dependency locking
- **API:** Minimal REST endpoints for verification

## Domain Model

**Game Leaderboard System** - chosen for being fun, engaging, and relatable.

### Initial Schema (V1)

**players table:**
- id (BIGINT, AUTO_INCREMENT, PRIMARY KEY)
- username (VARCHAR(50), UNIQUE, NOT NULL)
- email (VARCHAR(100), UNIQUE, NOT NULL)
- created_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

**matches table:**
- id (BIGINT, AUTO_INCREMENT, PRIMARY KEY)
- player_id (BIGINT, NOT NULL, FOREIGN KEY → players.id)
- score (INT, NOT NULL)
- played_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
- Indexes: player_id, played_at

### Initial Data (V2)

- 10 players
- 20 match records
- Minimal seed to get started

## Data Generation

**Script:** `scripts/generate-data.sh`
- Generates `players_historical.csv` (~100k players)
- Generates `matches_historical.csv` (~500k matches)
- Generates `matches_batch2.csv` (~50k matches with some duplicates)
- Large enough dataset to demonstrate table locking and performance impacts

## Exercise Progression

### Exercise 0: Setup & First Migration Run (5 min)
**Goal:** Understand the baseline project structure

- Clone repo, start Docker Compose
- Run `./gradlew bootRun` - app starts with V1 & V2 applied
- Verify via REST API that 10 players and 20 matches exist
- Explore `flyway_schema_history` table

**Learning:** Flyway basics, migration versioning, schema history tracking

---

### Exercise 1: Backfill Historical Data (10-15 min)
**Goal:** Load large dataset efficiently

- Run `generate-data.sh` to create CSV files
- Create V3 migration to load historical data
- Teams discuss approaches: LOAD DATA INFILE vs batched INSERTs
- Experience potential timeout scenario
- Learn about Flyway timeout configuration

**Learning:**
- Bulk data loading strategies
- Migration execution time estimation
- Transaction management for large datasets
- Timeout handling

---

### Exercise 2: Adding Safe Columns (5 min)
**Goal:** Understand safe additive changes

- Add nullable `country` column to players table
- Add nullable `game_mode` column to matches table
- Discuss why nullable is safe vs NOT NULL

**Learning:**
- Safe schema changes
- Additive migrations
- Why nullable columns don't block

---

### Exercise 3: Adding Indexes - Table Locking (10 min)
**Goal:** Experience table locking with large datasets

- Add index on `matches.score` for leaderboard queries
- Observe table locking with 500k rows
- Measure execution time
- Observe app behavior during migration

**Learning:**
- Index creation locking behavior
- DDL operation impacts
- ALGORITHM=INPLACE vs ALGORITHM=COPY
- Production downtime considerations

---

### Exercise 4: Checksum Mismatch Scenario (5-10 min)
**Goal:** Recover from edited migration file

**Setup:**
- Instructions tell them a "teammate" fixed a typo in V3
- They manually edit the V3 file (change comment/formatting)
- Try to run the app again

**What happens:**
- Flyway detects checksum mismatch
- Application fails to start

**Learning:**
- Flyway's checksum validation
- Why you NEVER edit applied migrations
- Using `flyway repair` to fix checksums
- Proper fix: create NEW migration instead

---

### Exercise 5: Failed Migration - Halfway Applied (15 min)
**Goal:** Recover from migration that failed midway

**Provided:** `broken-migrations/V6__add_achievements_BROKEN.sql`
```sql
CREATE TABLE achievements (...);

-- Syntax error - missing closing quote
INSERT INTO achievements VALUES (1, 'invalid syntax here;

-- This never runs
CREATE TABLE player_achievements (...);
```

**What happens:**
- Migration fails partway through
- `achievements` table exists, but `player_achievements` doesn't
- `flyway_schema_history` marks V6 as failed
- App won't start

**Learning:**
- Non-transactional DDL in MySQL
- Manual recovery process: fix SQL, use `flyway repair`, re-run
- Why migrations should be small and atomic
- Database state after partial failures

---

### Exercise 6: Dangerous Column Type Change (10 min)
**Goal:** Experience table locking during column modifications

**Instructions:** "Change `matches.score` from INT to BIGINT to support higher scores"

**Provided:**
```sql
ALTER TABLE matches MODIFY COLUMN score BIGINT NOT NULL;
```

**What happens:**
- With 500k rows, this takes noticeable time
- Table is locked during operation
- Impact on application availability

**Learning:**
- Table locking during ALTER COLUMN
- Execution time estimation
- Production strategies (blue-green, expand-contract pattern)
- When is it safe vs when you need different approach

---

### Exercise 7: Adding NOT NULL Without Backfill (10-15 min)
**Goal:** Understand safe multi-step pattern for constraints

**Instructions:** "Add a `region` column to players table, it should be required"

**Provided:** `broken-migrations/V8__add_region_NOT_NULL.sql`
```sql
ALTER TABLE players ADD COLUMN region VARCHAR(50) NOT NULL;
```

**What happens:**
- Migration fails because existing rows have NULL
- Leaves table in inconsistent state (column exists but migration marked failed)

**Learning:**
- Safe pattern: Add nullable → backfill data → add constraint
- Manual recovery from inconsistent state
- Multi-step schema changes
- Data validation before constraints

---

### Exercise 8: Renaming a Column (10 min)
**Goal:** Understand coordination between schema and code changes

**Instructions:** "Rename `username` to `player_name` for clarity"

**Provided:**
```sql
ALTER TABLE players CHANGE COLUMN username player_name VARCHAR(50) NOT NULL;
```

**What happens:**
- Migration succeeds
- Application code breaks (still references `username`)
- Tests fail, endpoints return errors

**Learning:**
- Schema changes must coordinate with code changes
- Expand-contract pattern for zero-downtime deploys
- Safe approach: add new column, dual-write, migrate code, remove old column
- Breaking vs non-breaking changes

---

### Exercise 9: Duplicate Key Violation & Idempotency (15 min)
**Goal:** Learn idempotency patterns for data migrations

**Instructions:** "Import another batch of historical match data"

**Provided:**
- `matches_batch2.csv` (~50k records, some overlap with existing data)
- `broken-migrations/V10__load_match_batch2.sql`

```sql
LOAD DATA LOCAL INFILE 'matches_batch2.csv'
INTO TABLE matches
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(player_id, score, played_at);
```

**What happens:**
- Migration fails on duplicate key (if unique constraint exists)
- OR succeeds but creates duplicate records (if no constraint)

**Learning:**
- Idempotency in data migrations
- `INSERT IGNORE` vs `ON DUPLICATE KEY UPDATE` vs `REPLACE INTO`
- When to add constraints to prevent duplicates
- Making migrations safe to re-run
- Trade-offs of each approach

**Discussion:** Should match data allow duplicates or not?

---

## Key Learning Topics Covered

1. **Flyway Fundamentals**
   - Naming conventions (V1__, V2__, etc.)
   - Versioning and ordering
   - Schema history tracking
   - Checksum validation

2. **Safe vs Risky Changes**
   - Additive changes (nullable columns, new tables)
   - Risky changes (renaming, type changes, NOT NULL)
   - Breaking vs non-breaking changes

3. **Table Locking & Performance**
   - DDL operations that lock tables
   - Index creation impacts
   - Execution time estimation
   - ALGORITHM options in MySQL
   - Production downtime considerations

4. **Constraints & Indexes**
   - Foreign keys
   - Unique constraints
   - Indexes for performance
   - When to add them, how they affect migrations

5. **Idempotency**
   - Why migrations must be repeatable
   - Patterns for data migrations
   - INSERT IGNORE, ON DUPLICATE KEY UPDATE
   - Handling duplicates

6. **Recovery Scenarios**
   - Checksum mismatches
   - Failed migrations stuck in history
   - Manual intervention (half-applied migrations)
   - Using `flyway repair`
   - Manual `flyway_schema_history` fixes

7. **Data Migrations**
   - Bulk loading strategies
   - Backfilling data safely
   - Transforming existing data
   - Transaction management
   - Timeout handling

8. **Production Considerations**
   - Execution time estimation
   - Timeout configuration
   - Zero-downtime deployment patterns
   - Expand-contract pattern
   - Coordinating schema and code changes

## Repository Structure

```
game-leaderboard-service/
├── README.md                           # Overview and setup instructions
├── EXERCISES.md                        # Exercise instructions (intentionally light)
├── SOLUTIONS.md                        # Detailed instructor guide (extract before upload)
├── build.gradle                        # Gradle build with Flyway plugin
├── settings.gradle
├── gradle/
├── gradlew, gradlew.bat
├── docker-compose.yml                  # MariaDB container
├── scripts/
│   ├── generate-data.sh                # Generate CSV files
│   └── reset-database.sh               # Nuclear option - wipe and restart
├── data/                               # Generated CSV files (gitignored)
├── broken-migrations/                  # Intentionally broken migrations for exercises
│   ├── V6__add_achievements_BROKEN.sql
│   ├── V8__add_region_NOT_NULL.sql
│   └── V10__load_match_batch2.sql
├── src/
│   ├── main/
│   │   ├── java/com/wise/leaderboard/
│   │   │   ├── LeaderboardApplication.java
│   │   │   ├── controller/
│   │   │   │   ├── PlayerController.java
│   │   │   │   └── MatchController.java
│   │   │   ├── model/
│   │   │   │   ├── Player.java
│   │   │   │   └── Match.java
│   │   │   ├── repository/
│   │   │   │   ├── PlayerRepository.java
│   │   │   │   └── MatchRepository.java
│   │   │   └── service/
│   │   │       └── LeaderboardService.java
│   │   └── resources/
│   │       ├── application.yml         # DB config, Flyway settings
│   │       └── db/migration/
│   │           ├── V1__Initial_schema.sql
│   │           └── V2__Seed_initial_data.sql
│   └── test/
│       └── java/com/wise/leaderboard/
│           └── LeaderboardApplicationTests.java
```

## Docker Compose Configuration

```yaml
version: '3.8'
services:
  mariadb:
    image: mariadb:11.2
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: leaderboard
      MYSQL_USER: leaderboard_user
      MYSQL_PASSWORD: leaderboard_pass
    ports:
      - "3306:3306"
    volumes:
      - mariadb-data:/var/lib/mysql
volumes:
  mariadb-data:
```

## Documentation Approach

### README.md
- Project overview (2-3 sentences)
- Prerequisites (Java 21, Docker, Gradle)
- Quick start commands
- How to verify it's working
- Useful commands (check Flyway history, reset database)
- Link to EXERCISES.md

### EXERCISES.md
Intentionally light on hand-holding. Each exercise includes:
- **Goal:** What you're trying to achieve (1-2 sentences)
- **Context:** Brief business scenario
- **Instructions:** Minimal steps, leaves room for interpretation
- **Discussion questions:** For teams to talk through

Example format:
```markdown
## Exercise 5: Recovery from Failed Migration

**Goal:** Fix a migration that failed partway through execution.

**Context:** A teammate wrote V6 to add achievements functionality, but it's failing.

**Instructions:**
1. Copy the provided V6 migration into your migrations folder
2. Try to start the application
3. Investigate what went wrong
4. Fix it and get the application running again

**Discussion:**
- What state is the database in after a failed migration?
- Why did some tables get created but not others?
- What's the recovery process?
```

### SOLUTIONS.md
Detailed instructor guide with:
- **Expected outcome** for each exercise
- **Common mistakes** teams make
- **Solution** with complete, correct code
- **Explanation** of why the approach works
- **Discussion points** to deepen understanding
- **Time estimate** for each exercise

This file will be extracted before uploading the repository to students.

## Application Features

### REST Endpoints (Minimal)

**PlayerController:**
- `GET /players` - List all players
- `GET /players/{id}` - Get player by ID
- `POST /players` - Create new player

**MatchController:**
- `GET /matches` - List recent matches
- `GET /matches/leaderboard` - Top scores
- `POST /matches` - Record new match

**Purpose:** Just enough to verify migrations work, not the focus of exercises.

### Application Configuration

**application.yml:**
```yaml
spring:
  datasource:
    url: jdbc:mariadb://localhost:3306/leaderboard
    username: leaderboard_user
    password: leaderboard_pass
  flyway:
    enabled: true
    baseline-on-migrate: true
    locations: classpath:db/migration
    command-line-args: --
    # Allow students to adjust timeouts during exercises
    placeholder-replacement: true
```

## Success Criteria

After completing this training, graduates should be able to:

1. Create and run Flyway migrations following Wise standards
2. Distinguish between safe and risky schema changes
3. Understand table locking and estimate migration execution time
4. Recover from common migration failures
5. Write idempotent data migrations
6. Explain expand-contract pattern for zero-downtime changes
7. Use `flyway repair` and manual recovery techniques
8. Consider production implications of schema changes

## Future Enhancements (Out of Scope)

- Advanced: pt-online-schema-change integration
- Advanced: Blue-green deployment simulation
- Multi-environment migrations (dev, staging, prod)
- Rollback strategies and compensating migrations
- Performance tuning with EXPLAIN plans
