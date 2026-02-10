# Database Migrations at Wise
## A Hands-On Journey Through Production Realities

**Training Session - 30 minutes**

---

## 👋 Welcome!

**Today's Adventure:**
- Learn how NOT to break production databases
- Understand Flyway and migration best practices
- Get hands-on with real scenarios (the fun kind of breaking things)

**What you'll leave with:**
- Confidence to write safe migrations
- Battle-tested recovery techniques
- War stories to tell at standup

---

## 🎯 Why This Matters

**Real Wise scenario:**
```
16:45 - Deploy starts
16:47 - Migration runs on 100M row table
16:48 - Table locked
16:49 - API timeouts
16:50 - Customers can't send money
16:51 - Everyone panics 😱
```

**Today we learn how to avoid becoming that person.**

---

## 🧰 What We're Building

**Game Leaderboard Service**
- Spring Boot + Flyway + MariaDB
- Simple domain: players, matches, scores
- Real migration scenarios
- Intentionally broken migrations (for science!)

**Why a game?**
- More fun than banking tables
- Same problems, less stress
- Easier to understand the data

---

## 📚 What's Flyway?

**The elevator pitch:**
- Version control for your database
- Tracks what's been applied
- Runs migrations in order
- Prevents "did I run this?" confusion

**Key concept:**
```
V1__Initial_schema.sql     ← Applied March 1st
V2__Add_new_column.sql     ← Applied March 5th
V3__Create_index.sql       ← Applied March 8th
```

Once applied = **NEVER EDIT**. Create new migration instead.

---

## 🚀 Let's Get Started!

**First 15 minutes: Hands-on setup**

We'll cover:
- ✅ Exercise 0: Clone & run the app
- ✅ Exercise 1: Load bulk data (backfill pattern)
- ✅ Exercise 2: Add safe columns
- ✅ Exercise 3: Create indexes
- 👀 Peek at `flyway_schema_history` table

**Goal:** Get comfortable with the happy path before we break things.

---

## 💻 Exercise 0: Setup (5 min)

**Your mission:**
```bash
# Clone the repo
git clone https://github.com/simon-at-wise/wisestart-db-migration.git
cd wisestart-db-migration

# Start database
docker-compose up -d

# Run the app
./gradlew bootRun
```

**Check it works:**
```bash
curl http://localhost:8080/players
curl http://localhost:8080/matches/leaderboard
```

You should see 10 players and 20 matches!

---

## 📊 Exercise 1: Bulk Data Loading (5 min)

**Scenario:** Marketing found historical data. Load 100k players + 500k matches.

**Steps:**
1. Generate CSV files: `./scripts/generate-data.sh`
2. Create `V3__Load_historical_data.sql` migration
3. Use `LOAD DATA LOCAL INFILE` (fastest way)
4. Watch it run (might take 15-30 seconds)

**Key learning:** Large data migrations need different approaches than small inserts.

---

## ✅ Exercise 2: Safe Columns (2 min)

**Scenario:** Product wants to track player country and game mode.

**Create V4 and V5:**
```sql
ALTER TABLE players ADD COLUMN country VARCHAR(2) NULL;
ALTER TABLE matches ADD COLUMN game_mode VARCHAR(20) NULL;
```

**Why is this safe?**
- Nullable = no backfill required
- Fast (metadata-only change)
- No table locks
- No data migration

**Rule:** Nullable columns = safe. NOT NULL = careful!

---

## 🔍 Exercise 3: Index Creation (3 min)

**Scenario:** Leaderboard queries are slow. Add index on score.

**Create V6:**
```sql
CREATE INDEX idx_matches_score ON matches(score);
```

**Watch it run.** Time it. With 500k rows, this takes several seconds.

**Questions to discuss:**
- Was the table locked?
- Could you query during creation?
- What happens in production with 100M rows?

---

## 🔬 Let's Peek: flyway_schema_history

**Connect to database:**
```bash
docker exec -it leaderboard-db mariadb -u leaderboard_user -pleaderboard_pass leaderboard
```

**Check migration history:**
```sql
SELECT installed_rank, version, description,
       success, execution_time
FROM flyway_schema_history;
```

**What you see:**
- Every migration tracked
- Checksums for validation
- Execution time
- Success/failure status

---

## 🎓 Knowledge Check: The Happy Path

**What we learned:**
- ✅ Flyway tracks migrations automatically
- ✅ Bulk data? Use LOAD DATA INFILE
- ✅ Nullable columns are safe
- ✅ Indexes take time on large tables
- ✅ Check `flyway_schema_history` to see what's applied

**Now let's break things! 😈**

---

## ⚠️ When Things Go Wrong

**The three horsemen of migration apocalypse:**

1. **Checksum Mismatch** - "Someone edited an applied migration"
2. **Failed Migration** - "SQL error midway through"
3. **Timeout** - "Migration took too long"

**Good news:** All fixable if you know the patterns!

**Bad news:** You WILL encounter these. Better to learn here than in production.

---

## 🔧 Exercise 4: Checksum Mismatch (3 min)

**Scenario:** Your teammate "fixed" a typo in an old migration.

**Try this:**
1. Edit `V2__Seed_initial_data.sql` (change a comment)
2. Restart the app: `./gradlew bootRun`
3. 💥 BOOM! Checksum mismatch

**Fix it:**
```bash
# Revert the change
git checkout src/main/resources/db/migration/V2__Seed_initial_data.sql

# Repair Flyway history
./gradlew flywayRepair

# Restart
./gradlew bootRun
```

**The lesson:** NEVER edit applied migrations. Create new ones.

---

## 🚨 Exercise 5: Failed Migration (5 min)

**Scenario:** A migration fails halfway through. The database is in a weird state.

**Try this:**
1. Copy `broken-migrations/V6__add_achievements_BROKEN.sql` to migrations folder
2. Try to start the app
3. 💥 SQL syntax error!

**What happened?**
- `achievements` table was created ✅
- INSERT failed with syntax error ❌
- `player_achievements` table never created ❌

**Database state = partial!**

---

## 🔧 Recovering from Failed Migrations

**Check the damage:**
```sql
SHOW TABLES;  -- achievements exists, player_achievements doesn't
SELECT * FROM flyway_schema_history WHERE version = '6';  -- success = 0
```

**Fix it:**
1. Fix the SQL error in the migration file
2. Run `./gradlew flywayRepair` (marks as pending)
3. Restart app (re-runs the migration)

**Pro tip:** MySQL DDL is NOT transactional. PostgreSQL is better for this.

---

## ⏱️ Exercise 6: Timeout Scenarios

**What causes timeouts?**
- Large table alterations (100M+ rows)
- Index creation on huge tables
- Bulk data loads
- Table locks blocking other queries

**Solutions:**
- Increase Flyway timeout: `spring.flyway.placeholders.timeout=600`
- Split migrations into smaller chunks
- Use online schema change tools (pt-online-schema-change)
- Run during low-traffic windows

**Reality check:** Some migrations just take time. Plan accordingly.

---

## 🎯 Core Knowledge Complete!

**You now know:**
- ✅ How Flyway tracks migrations
- ✅ Safe vs risky schema changes
- ✅ How to recover from checksum mismatches
- ✅ How to recover from failed migrations
- ✅ Why timeouts happen and how to handle them

**This is 80% of what you need for production.**

The rest is edge cases and optimization. Let's peek at those...

---

## 🔄 Advanced Topics (Quick Overview)

**The exercises that remain (optional/homework):**

**Exercise 7:** Column type changes (INT → BIGINT)
- Requires table rebuild
- Locks table during change
- "Expand-contract" pattern for zero-downtime

**Exercise 8:** Adding NOT NULL constraints
- WRONG: `ALTER TABLE ADD COLUMN region NOT NULL;` ❌
- RIGHT: Add nullable → backfill data → add constraint ✅

---

## 💥 More Edge Cases

**Exercise 9:** Renaming columns (breaking changes)
- Schema change succeeds
- Application code breaks
- Need to coordinate deploys
- "Expand-contract" pattern saves the day

**Exercise 10:** Duplicate keys & idempotency
- Data migrations should be re-runnable
- `INSERT IGNORE` vs `ON DUPLICATE KEY UPDATE`
- Handle failures gracefully

**Don't stress these now.** They're in the repo for later practice.

---

## 📀 Bonus: How Data is Stored

**Why do column changes take so long?**

```
Table on disk:
[Row 1: ID|Name|Score]
[Row 2: ID|Name|Score]
[Row 3: ID|Name|Score]
...millions more...
```

**Changing INT → BIGINT:**
- MySQL reads every row
- Rewrites every row with new format
- Updates indexes
- Locks table during rewrite

**100M rows = 10+ minutes of downtime.** That's why we use expand-contract!

---

## 🎓 Production Best Practices

**Before running migrations in production:**

1. ✅ Test on production-SIZE data (not just a few rows)
2. ✅ Estimate execution time
3. ✅ Understand locking behavior
4. ✅ Have a rollback plan (usually = new migration)
5. ✅ Monitor during deployment
6. ✅ Run during low-traffic windows if possible
7. ✅ Use feature flags to decouple schema from code

**Remember:** Breaking prod = learning opportunity = résumé builder 😅

---

## 🛠️ Useful Commands Cheat Sheet

**Application:**
```bash
./gradlew bootRun              # Start app
./gradlew test                 # Run tests
./scripts/reset-database.sh    # Nuclear option
```

**Flyway:**
```bash
./gradlew flywayInfo      # Check migration status
./gradlew flywayRepair    # Fix checksums/failed migrations
./gradlew flywayValidate  # Validate migrations
```

**Database:**
```bash
docker exec -it leaderboard-db mariadb -u leaderboard_user -pleaderboard_pass leaderboard
```

---

## 📚 Additional Resources

**In the repo:**
- `README.md` - Complete setup guide
- `EXERCISES.md` - All 10 exercises with hints
- `SOLUTIONS.md` - Instructor guide (don't peek yet!)
- `broken-migrations/` - Pre-broken files for practice

**Further reading:**
- [Flyway Documentation](https://flywaydb.org/documentation/)
- [MySQL Online DDL](https://dev.mysql.com/doc/refman/8.0/en/innodb-online-ddl.html)
- [Expand-Contract Pattern](https://martinfowler.com/bliki/ParallelChange.html)

---

## 🎯 Your Mission (If You Choose to Accept)

**Today:**
- ✅ Finish exercises 0-6 (core knowledge)
- ✅ Try to break and fix things

**This week:**
- 🏠 Complete exercises 7-10 at your own pace
- 🏠 Run through the scenarios again for practice

**In production:**
- 🚀 Write your first migration with confidence
- 🚀 Help teammates recover from migration issues
- 🚀 Share your war stories

**Remember:** Everyone breaks migrations. The pros just know how to fix them faster.

---

## ❓ Questions?

**Common questions we didn't cover:**

- What about rolling back migrations?
- How do we handle migrations across multiple services?
- What if I need to migrate 1 billion rows?
- Can I test migrations in CI/CD?

**Let's discuss!**

Also: The repo issues page is open for questions later.

---

## 🎉 Thank You!

**You're now a migration warrior!** 🗡️

**Key takeaways:**
- Flyway is your friend
- Always test with production-size data
- Recovery is a skill, not a failure
- When in doubt, ask for help

**Repository:**
https://github.com/simon-at-wise/wisestart-db-migration

**Questions? Feedback?**
Find me on Slack or open a GitHub issue.

Now go forth and migrate safely! 🚀

---

## 🎬 Appendix: Session Timing

**Suggested schedule (30 minutes total):**

- 0-10 min: Slides 1-7 (Intro, why it matters, Flyway basics)
- 10-25 min: Exercises 0-3 + Flyway peek (hands-on setup)
- 25-30 min: Slides 8-12 (When things go wrong intro)
- 30-38 min: Exercises 4-6 (break things, fix them)
- 38-43 min: Slides 13-15 (Advanced topics overview)
- 43-45 min: Slides 16-18 (Best practices, Q&A)

**Total with exercises: ~45 minutes**
**Pure presentation: 30 minutes**

Adjust based on audience questions and energy!
