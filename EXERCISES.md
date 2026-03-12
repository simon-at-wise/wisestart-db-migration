# Database Migration Training Exercises

This document contains hands-on exercises to practice database migration patterns using the Game Leaderboard application.

## Prerequisites

- Complete the README.md setup instructions
- Familiarize yourself with the codebase structure
- Understand basic SQL and database concepts

## Exercise 0: Understand the Service

**Objective**: Check that the service runs as you'd expect

Use the readme to make sure that:
- Service can run
- You can query the endpoints
- You can connect to the database and see the three tables

**Output**: Use Describe flyway_schema_history to see the table, and then post to Slack with an explanation of one of the columns that hasn't been explained yet by others

---

## Exercise 1: Understanding Flyway Repair and why Migrations are Immutable

**Objective**: Understanding common migration issues

**Tools**: 
- Connection to the database server and ability to read and modify the data (through mysql or the database panel in IntelliJ)
- Migration files in /src/main/resources/db/migration

**Steps**:
1. Open the migration folder and check out migrations V1 and V2
2. Update V2__Seed_initial_data.sql with an extra item
3. Run the application
4. See the error message.

Questions: 
- Flyway migration has failed. Why? How?
- What will be required to run this migration again?

Steps:
5. Remove the entry for V2 in the flyway_schema (DELETE from flyway_schema_history where ..) 
6. Run the application again. 
7. If it succeeded, check the players table.
8. If it failed, fix your syntax then repeat step 5-6-7

Questions:
- What has happened during startup this time?
- Should we have emptied the table first? Should we have created a separate migration? Are there other solutions?

Steps:
9. Change the migration file again. 
10. Run the application again. You'll get the same error. Check the flyway schema to see what has changed.
11. Now add flyway.repair() to the FlywayMigrationConfig and run again.

Questions:
- What is different in the flyway schema this time? 
- What is the difference between removing and repairing?
- What should we do instead of changing the previous migration? 
- When should we use which approach?

Before you continue, reset the database with the reset script from the Readme.

**Learnings**: 
- Don't have repair() on by default, but know to use it to 'fix' small mistakes.
- Know how to fix your migrations locally and on staging while you're still developing / finding out what you need to do.

**Output**: Post your flyway migration table after successfully running the migration again. And formulate at least one alternative solution to add an extra element.

**Note**: Make sure to remove flyway.repair() again before you continue because it's not supposed to remain in production code!

---

## Exercise 2: Add Player Email Field

**Objective**: Learn to add a new non-null column with a default value, and to update the related entities.

**Scenario**: The product team wants to send email notifications to players. Add an email field to the players table, and update the APIs accordingly.

**Requirements**:
1. Email should be non-null
2. Email should have a unique constraint, and since we will want to search by email, make sure it's indexed
3. Use a safe migration pattern for adding non-null columns
4. Fill data from data/original_player_emails.csv. Existing players who don't have an email should get a default email in the format: `player_{id}@example.com`

**Tools**
- New migration file(s) in `src/main/resources/db/migration/`
- PlayerService and PlayerController to show the email.

**Steps**:
1. Create a new migration file in `src/main/resources/db/migration/`
2. Add the email column as nullable first
3. Backfill data for existing players from /data/original_player_emails.csv using the migration
4. Add the NOT NULL constraint
5. Add a unique constraint
6. Update the Player entity to include the email field
7. Update PlayerService to handle email when creating players
8. Run the application and verify the migration and updated endpoints

**Validation**:
- Run `./gradlew bootRun` and check logs for successful migration
- Query the database: `SELECT id, username, email FROM players;`
- Verify existing players in the database have emails
- Verify existing players have emails when querying the /players API
- Create a new player through the API and verify email is required

**Learning Points**:
- Why we add columns as nullable
- Importance of backfilling data
- Adding constraints after data is populated
- Entity-database synchronization

**Output**: Write to the Slack channel your new Flyway_schema_history and the result of `describe players`

---

## Exercise 3: Backfill large amount of player data

**Objective**: Add a large amount of data to an existing database table

**Scenario**: Now that the new system is complete and working, we wish to import a large amount of player data.

**Requirements**: 
1. Find a way to import the new player data from /data/players_historical.csv into the players table

**Tools**:
- Consider using your AI agent or alternatives to come up with solutions.
- If it looks like things take a long time, consider how to speed them up.

**Steps**:
1. Generate the new player data by running `scripts/generate-data.sh` 
2. Find a way to import all the player data into the players table. Do not use LOAD DATA.

**Validation**:
- Check the database table to see that all 100.000 new players have been imported.
- See that those players are returned through the API

**Learning Points**:
- Understand the different tools available to do such import

**Discuss**: What are the pros and cons of the options you have? Why can't we use LOAD DATA in practice?

**Output**: Slack how long it took for you to migrate all the data. Summarize the issues you faced and what solutions you chose and why.

---

## Exercise 4a: Add index to players - Unhealthy data

**Objective**: Practice adding an index to a table where data isn't healthy.

**Scenario**: We need to select players by username. Unfortunately, it looks like some of our users are duplicates because the previous system allowed for this.

**Steps**:
1. Add a new migration file that adds a unique key to the players.username column. Make sure to use 'if not exists' in this query
2. Run the migration - Check that it succeeds.
3. If it fails: Come up with a practical solution for the duplicate usernames, and apply it using the same V4 migration.
4. Run it again and show that it works.

**Learning Points**:
- Make sure to use if not exists when creating an index.
- Make sure that the data is healthy before adding an index
- Understand the impact of adding an index. Does it lock the table? How long will it take? What happens if the migration times out?

**Output**: Write your index migration SQL to the Slack channel. How long did it take to run? List the issues you ran into and what you did to solve them.

---

## Exercise 4b: Add index to matches - Large Dataset

**Objective**: Practice adding an index to a table that is large.

**Scenario**: We have added lots of player matches, and looking up stuff is getting slow. We have to add an index to allow better performance.

**Steps**:
1. Add data to the matches table by running scripts/insert_match_data.sh. It should add 1 mil randomized entries to the matches table
2. Test the 'Find By' and 'getTopScores' endpoints in the MatchController. Measure how long some take.
3. Create a migration to add an index to the timeStarted and timeEnded columns
4. Run the migration. Discuss the factors that impact how long this will take. What happens with the table in the meantime?
5. Test the endpoints again. Did the performance improve? What else could improve it if it needs to be further improved?


**Learning Points**:
- Make sure to use if not exists when creating an index.
- Know what to do when you hit a timeout
- Understand the impact of adding an index. Does it lock the table? How long will it take? What happens if the migration times out?

**Output**: Write your index migration SQL to the Slack channel. How much was the improvement? List the issues you ran into and what you did to solve them.

## Exercise 5: Rename Player Username

**Objective**: Learn safe column renaming techniques.

**Scenario**: The team decides "username" should be called "player_name" for clarity.

**Requirements**:
1. Rename the column without downtime
2. Support both old and new application versions during deployment
3. Use the expand-contract pattern

**Steps**:
1. **Migration 1 - Expand**: Add new `player_name` column
2. **Migration 2**: Backfill data from username to player_name
3. **Migration 3**: Add trigger to keep columns in sync
4. Update application code to use player_name
5. Deploy and verify both columns work
6. **Migration 4 - Contract**: Drop username column and trigger

**Validation**:
- After expand phase: Both columns exist and stay in sync
- After contract phase: Only player_name exists
- No data loss during the process
- Application works throughout the migration

**Learning Points**:
- Expand-contract pattern
- Database triggers for data synchronization
- Zero-downtime deployments
- Backwards compatibility

---

## Exercise 6: Add Soft Delete Support

**Objective**: Implement soft delete pattern for data retention.

**Scenario**: Players should be "deleted" but retained for compliance and analytics.

**Requirements**:
1. Add deleted_at column to players table
2. Update queries to filter out deleted players
3. Create methods for soft delete and restore
4. Ensure referential integrity

**Steps**:
1. Create migration to add deleted_at (TIMESTAMP, nullable)
2. Update Player entity with @Where annotation
3. Update PlayerRepository with soft delete method
4. Update PlayerService to use soft delete
5. Add restore functionality
6. Test delete and restore operations

**Validation**:
- Deleted players don't appear in normal queries
- Deleted players' data is retained in database
- Can restore deleted players
- Foreign key relationships handled correctly

**Learning Points**:
- Soft delete vs hard delete
- JPA @Where clause
- Data retention strategies
- Compliance considerations

---

## At this point, you've reached all the exercises I've prepared.
## the rest are AI generated exercises that may or may not be working.



## Exercise 6: Add Game Metadata

**Objective**: Practice adding multiple columns and working with JSON data.

**Scenario**: Game sessions need to store additional metadata like game mode, duration, and settings.

**Requirements**:
1. Add `game_mode` column (VARCHAR, values: 'casual', 'ranked', 'tournament')
2. Add `duration_seconds` column (INTEGER, nullable)
3. Add `settings` column (JSON, nullable) for flexible configuration storage
4. Set default game_mode to 'casual' for existing games

**Steps**:
1. Create a new migration file
2. Add the three new columns
3. Backfill game_mode for existing games
4. Update the Game entity with new fields
5. Update GameService to handle new fields
6. Test with different game modes and settings

**Validation**:
- Verify all existing games have game_mode = 'casual'
- Create new games with different modes
- Store and retrieve JSON settings (e.g., `{"difficulty": "hard", "map": "arena_1"}`)

**Learning Points**:
- Working with ENUM-like values in PostgreSQL
- Using JSON columns for flexible data
- Default values vs nullable columns
- When to use structured vs unstructured data

---


## Exercise 7: Add Score History Table

**Objective**: Practice creating new tables with foreign key relationships.

**Scenario**: Track historical changes to player scores for audit purposes.

**Requirements**:
1. Create a `score_history` table
2. Record every score change with timestamp
3. Link to the player via foreign key
4. Include old_score, new_score, and reason fields

**Table Structure**:
```sql
score_history:
- id (BIGSERIAL PRIMARY KEY)
- player_id (BIGINT, FK to players)
- old_score (INTEGER)
- new_score (INTEGER)
- reason (VARCHAR)
- changed_at (TIMESTAMP)
```

**Steps**:
1. Create migration with new table
2. Add foreign key constraint to players table
3. Add indexes on player_id and changed_at
4. Create ScoreHistory entity
5. Create ScoreHistoryRepository
6. Update ScoreService to record changes
7. Test score updates and query history

**Validation**:
- Create players and update scores multiple times
- Query score history: `SELECT * FROM score_history ORDER BY changed_at DESC;`
- Verify foreign key prevents orphaned records
- Check that indexes improve query performance

**Learning Points**:
- Creating tables with relationships
- Foreign key constraints
- Index strategy for common queries
- Audit trail patterns

---

## Exercise 8: Add Composite Index

**Objective**: Learn to identify and create performance-improving indexes.

**Scenario**: Queries filtering games by status and date are slow. Add an optimized index.

**Requirements**:
1. Analyze the slow query pattern
2. Create a composite index on (status, created_at)
3. Measure query performance before and after

**Steps**:
1. Insert test data (at least 10,000 games)
2. Run EXPLAIN ANALYZE on: `SELECT * FROM games WHERE status = 'completed' AND created_at > NOW() - INTERVAL '7 days';`
3. Create migration with composite index
4. Run EXPLAIN ANALYZE again
5. Compare execution plans

**Validation**:
- Query plan shows index usage
- Query execution time improves significantly
- Index doesn't negatively impact INSERT performance

**Learning Points**:
- When to use composite indexes
- Column order in composite indexes matters
- EXPLAIN ANALYZE for query optimization
- Trade-offs between read and write performance

---

## Exercise 9: Migrate to UUID Primary Keys

**Objective**: Practice complex schema changes (changing primary key type).

**Scenario**: System needs to support distributed ID generation. Migrate from BIGSERIAL to UUID.

**Requirements**:
1. Migrate players table to use UUID primary keys
2. Update all foreign key references
3. Maintain data integrity throughout
4. Use blue-green deployment strategy

**Steps**:
1. **Migration 1**: Add uuid column to players table
2. **Migration 2**: Backfill UUIDs for existing players
3. **Migration 3**: Add uuid column to referencing tables (scores, score_history)
4. **Migration 4**: Backfill foreign key UUIDs
5. **Migration 5**: Update application to use UUIDs
6. **Migration 6**: Drop old ID columns and rename uuid to id
7. **Migration 7**: Recreate foreign key constraints

**Validation**:
- All relationships maintained
- No data loss
- Application works with UUIDs
- Old integer IDs no longer exist

**Learning Points**:
- Complex multi-step migrations
- Handling foreign key dependencies
- Different primary key strategies
- Production migration planning

**Note**: This is an advanced exercise. Consider doing it in a separate branch.

---

## Exercise 8: Add Database View

**Objective**: Learn to create and use database views for complex queries.

**Scenario**: Create a leaderboard view that combines player and score data.

**Requirements**:
1. Create a view showing top players with their stats
2. Include: username, total_score, games_played, average_score, rank
3. Make view queryable from Spring Data

**Steps**:
1. Create migration with CREATE VIEW statement
2. Add corresponding @Immutable entity
3. Create read-only repository
4. Create service method to query view
5. Add REST endpoint to expose leaderboard

**View Definition**:
```sql
CREATE VIEW leaderboard AS
SELECT
    p.id,
    p.username,
    p.total_score,
    COUNT(s.id) as games_played,
    AVG(s.score) as average_score,
    RANK() OVER (ORDER BY p.total_score DESC) as rank
FROM players p
LEFT JOIN scores s ON p.id = s.player_id
GROUP BY p.id, p.username, p.total_score;
```

**Validation**:
- Query view directly: `SELECT * FROM leaderboard LIMIT 10;`
- Access via REST API
- Verify data accuracy
- Check that view updates when underlying data changes

**Learning Points**:
- When to use views vs tables
- Window functions (RANK)
- Mapping views to JPA entities
- Read-only data access patterns

---

## Exercise 9: Implement Database Partitioning

**Objective**: Learn table partitioning for improved performance at scale.

**Scenario**: The games table grows very large. Partition by created_at for better query performance.

**Requirements**:
1. Partition games table by month
2. Create partitions for current and future months
3. Set up automatic partition creation
4. Migrate existing data to partitions

**Steps**:
1. **Migration 1**: Create new partitioned games table
2. **Migration 2**: Migrate data from old table to partitioned table
3. **Migration 3**: Create partitions for next 12 months
4. **Migration 4**: Drop old table and rename partitioned table
5. Test queries across partitions
6. Verify partition pruning in execution plans

**Partitioning Strategy**:
```sql
CREATE TABLE games_partitioned (
    LIKE games INCLUDING ALL
) PARTITION BY RANGE (created_at);

CREATE TABLE games_y2024m01 PARTITION OF games_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

**Validation**:
- Query EXPLAIN shows partition pruning
- Insert data and verify it goes to correct partition
- Query performance improves for date-range queries
- Check partition sizes: `SELECT * FROM pg_partition_tree('games_partitioned');`

**Learning Points**:
- Table partitioning strategies
- Partition pruning
- Maintenance of partitioned tables
- When partitioning makes sense

---

## Additional Challenges

### Challenge 1: Migration Rollback
- Create a migration that can be safely rolled back
- Practice writing DOWN migrations
- Test rollback scenarios

### Challenge 2: Data Migration with Transformation
- Migrate data while transforming values
- Handle edge cases and validation
- Ensure data quality post-migration

### Challenge 3: Performance Testing
- Create performance benchmarks
- Compare query performance before/after optimizations
- Use tools like pgbench or JMeter

### Challenge 4: Blue-Green Deployment
- Design a migration that supports blue-green deployment
- Ensure both old and new application versions work during transition
- Plan the complete deployment strategy

---

## Best Practices Checklist

When working through these exercises, ensure you:

- [ ] Test migrations on local database first
- [ ] Write reversible migrations when possible
- [ ] Add appropriate indexes for foreign keys
- [ ] Document complex migrations with comments
- [ ] Use transactions for data migrations
- [ ] Verify data integrity after migrations
- [ ] Check for locking issues on large tables
- [ ] Plan for zero-downtime deployments
- [ ] Keep migrations idempotent when possible

---

## Resources

- [Flyway Documentation](https://flywaydb.org/documentation/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Spring Data JPA Reference](https://docs.spring.io/spring-data/jpa/docs/current/reference/html/)
- [Database Migrations Best Practices](https://www.martinfowler.com/articles/evodb.html)

---

## Getting Help

If you get stuck:
1. Check the migration error messages in application logs
2. Query the Flyway schema history: `SELECT * FROM flyway_schema_history;`
3. Use `EXPLAIN ANALYZE` to understand query performance
4. Review PostgreSQL logs for detailed error information
5. Consult the main README.md for setup issues

Happy migrating!
