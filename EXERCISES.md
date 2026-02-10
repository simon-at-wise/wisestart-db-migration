# Database Migration Training Exercises

This document contains hands-on exercises to practice database migration patterns using the Game Leaderboard application.

## Prerequisites

- Complete the README.md setup instructions
- Familiarize yourself with the codebase structure
- Understand basic SQL and database concepts

## Exercise 1: Add Player Email Field

**Objective**: Learn to add a new non-null column with a default value.

**Scenario**: The product team wants to send email notifications to players. Add an email field to the players table.

**Requirements**:
1. Email should be non-null
2. Email should have a unique constraint
3. Use a safe migration pattern for adding non-null columns
4. Existing players should get a default email in the format: `player_{id}@example.com`

**tools**
- generate the backfill data through `python ./scripts/generate-data.sh`
- Look up how to use 'LOAD DATA LOCAL INFILE'


**Steps**:
1. Create a new migration file in `src/main/resources/db/migration/`
2. Add the email column as nullable first
3. Backfill data for existing players (generate through ./scripts/generate-data.sh)
4. Add the NOT NULL constraint
5. Add a unique constraint
6. Update the Player entity to include the email field
7. Update PlayerService to handle email when creating players
8. Run the application and verify the migration

**Validation**:
- Run `./gradlew bootRun` and check logs for successful migration
- Query the database: `SELECT id, username, email FROM players;`
- Verify existing players have default emails
- Create a new player and verify email is required

**Learning Points**:
- Why we add columns as nullable first
- Importance of backfilling data
- Adding constraints after data is populated
- Entity-database synchronization

---

## Exercise 2: Add Game Metadata

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

## Exercise 3: Rename Player Username

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

## Exercise 4: Add Score History Table

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

## Exercise 5: Add Composite Index

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

## Exercise 6: Migrate to UUID Primary Keys

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

## Exercise 7: Add Soft Delete Support

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

- [ ] Name migrations descriptively with timestamp prefix
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
