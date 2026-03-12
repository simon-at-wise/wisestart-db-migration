# Game Leaderboard Service - Database Migration Training

A Spring Boot training project designed to teach database migration best practices through hands-on exercises. Build for training new software engineers at Wise.

## What This Is

This is an educational project simulating a game leaderboard system. Teams work through progressively challenging database migration scenarios, learning:

- Flyway fundamentals
- Safe vs risky schema changes
- Table locking and performance impacts
- Recovery from failed migrations
- Idempotent data migrations
- Production deployment patterns

**Target audience:** Software engineers new to production database migrations.

**Time required:** 45-60 minutes of hands-on exercises.

## Prerequisites

- **Java 21** - [Download here](https://adoptium.net/)
- **Docker & Docker Compose** - [Download here](https://docs.docker.com/get-docker/)
- **Basic SQL knowledge** - Understanding of SELECT, INSERT, CREATE TABLE

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd wisestart-db-migration
```

### 2. Start Database

```bash
docker-compose up -d
```

Wait ~10 seconds for MariaDB to initialize.

### 3. Run Application

```bash
./gradlew bootRun
```

You should see:
```
Started LeaderboardApplication in X.XXX seconds
```

### 4. Verify It Works

```bash
# List all players (should see 10)
curl http://localhost:8080/players

# View leaderboard (top scores)
curl http://localhost:8080/matches/leaderboard

# Check server health
curl http://localhost:8080/actuator/health
```

### 5. Explore Database

```bash
docker exec -it leaderboard-db mariadb -u leaderboard_user -pleaderboard_pass leaderboard
```

You can also use the built in database explorer in IntelliJ:
Add a new MariaDB database connection with host `localhost:3316` and the username/password from the service application.yml file

```sql
-- See applied migrations
SELECT * FROM flyway_schema_history;

-- Explore tables
SHOW TABLES;
DESCRIBE players;
DESCRIBE matches;

-- Exit
exit;
```

## Project Structure

```
wisestart-db-migration/
├── data/
│   └── original_player_emails.csv      # used for filling data in exercise 2
├── src/main/
│   ├── java/com/wise/leaderboard/     # Application code
│   └── resources/
│       ├── application.yml             # Configuration
│       └── db/migration/               # Flyway migrations
│           ├── V1__Initial_schema.sql
│           └── V2__Seed_initial_data.sql
├── scripts/
│   ├── generate-data.sh                # Generate CSV test data
│   └── reset-database.sh               # Reset everything
├── broken-migrations/                  # Intentionally broken migrations for exercises
├── EXERCISES.md                        # Exercise instructions
└── docker-compose.yml                  # Database configuration
```

## Exercises

See **[EXERCISES.md](EXERCISES.md)** for the complete list of hands-on exercises.

### Exercise Overview

1. **Setup** - Get everything running
2. **Backfill Data** - Load 100k+ rows efficiently
3. **Safe Columns** - Add nullable columns
4. **Index Creation** - Experience table locking
5. **Checksum Mismatch** - Recover from edited migrations
6. **Failed Migrations** - Handle partial failures
7. **Column Type Changes** - Understand locking impact
8. **NOT NULL Constraints** - Learn multi-step patterns
9. **Breaking Changes** - Coordinate schema and code
10. **Duplicate Keys** - Write idempotent migrations

## Useful Commands

### Application

```bash
# Start application
./gradlew bootRun

# Run tests
./gradlew test

# Clean build
./gradlew clean build
```

### Resetting the Database when you messed up

```bash
# Reset everything (nuclear option)
./scripts/reset-database.sh

```

### Flyway
For if you're lazy, this will show the flyway status:
```bash
# Show migration status
./gradlew flywayInfo
```

### Data Generation

```bash
# Generate CSV files for exercises
./scripts/generate-data.sh

# Output: data/players_historical.csv, data/matches_historical.csv, data/matches_batch2.csv
```

## REST API Endpoints

### Players

- `GET /players` - List all players
- `GET /players/{id}` - Get player by ID
- `POST /players` - Create new player
  ```json
  {
    "username": "player123",
    "email": "player@example.com" // after exercise 3
  }
  ```

### Matches

- `GET /matches` - List recent matches (default 20)
- `GET /matches?limit=50` - List recent matches with custom limit
- `GET /matches/leaderboard` - Top scores (default 10)
- `GET /matches/leaderboard?limit=20` - Top scores with custom limit
- `POST /matches` - Record new match
  ```json
  {
    "playerId": 1,
    "score": 2500,
    "difficulty": "hard",
    "timeStarted": "2024-01-25T10:00:00",
    "timeEnded": "2024-01-25T10:25:00",
    "settings": {
      "sound": true,
      "music": false,
      "hints": false
    },
    "maxLevel": 9,
    "experienceGained": 625,
    "powerups": ["double_points", "shield", "speed_boost"],
    "feedbackScore": 5
  }
  ```
  Note: Only `playerId` and `score` are required. All other fields are optional.

### Health

- `GET /actuator/health` - Application health status

## Performance Testing

This project is configured with a **5MB InnoDB buffer pool** (the minimum allowed size) to simulate realistic production performance characteristics where data must be read from disk.

### Why This Matters

In production databases with large tables:
- Buffer pool may be 1-8GB, but tables can be 100s of GB
- Most queries hit disk, not memory cache
- Index creation can take minutes or hours
- Schema changes can lock tables for extended periods

## Technology Stack

- **Spring Boot 3.2.2** - Application framework
- **Java 21** - Programming language
- **Flyway** - Database migration tool
- **MariaDB 11.2** - Database (MySQL-compatible)
- **Gradle 8.5** - Build system
- **Lombok** - Boilerplate reduction
- **Spring Data JPA** - Database access

## Troubleshooting

### Application won't start

**Symptom:** "Connection refused" or "Unknown database"

**Solution:**
Check database is running and restart the docker containers if needed

### Port already in use

**Symptom:** "Port 3316 is already allocated"

**Solution:**
This project uses port 3316 to avoid conflicts with other MariaDB services running on the default port 3306. If you still encounter port conflicts, you can change the port mapping in both `docker-compose.yml` and `application.yml`, or you can stop existing docker containers on that port.

### Migration checksum mismatch

**Symptom:** "Migration checksum mismatch for migration version X"

**Solution:**
```bash
# See which migration has mismatch
./gradlew flywayInfo

# If you edited a migration file, revert it
git checkout -- src/main/resources/db/migration/VX__*.sql

# Repair checksums
add flyway.repair() to your FlywayMigrationConfig.

# Restart
./gradlew bootRun
```

### Migration failed midway

**Symptom:** "Migration VX failed" or application won't start

**Solution:**
```bash
# Check which migration failed
./gradlew flywayInfo

# Fix the SQL in the migration file

# Repair (marks failed migration as pending)
add flyway.repair() to your FlywayMigrationConfig.

# Restart (will re-run the migration)
./gradlew bootRun
```

### Need to start over

**Symptom:** Database is in unknown state, you broke it and can't figure out how to restore it.

**Solution:**
```bash
# Nuclear option - reset everything
./scripts/reset-database.sh

# Clean build
./gradlew clean

# Start fresh
./gradlew bootRun
```

## Common Pitfalls

1. **Editing applied migrations** - Never edit a migration that's been applied. Create a new one.
2. **Forgetting to start Docker** - Application needs database running first.
3. **Not waiting for database** - Give MariaDB 10 seconds to initialize.
4. **Timeout on large data loads** - Adjust Flyway timeout for bulk operations.

## Learning Resources

- [Flyway Documentation](https://flywaydb.org/documentation/)
- [MySQL Online DDL](https://dev.mysql.com/doc/refman/8.0/en/innodb-online-ddl.html)
- [Spring Boot + Flyway](https://docs.spring.io/spring-boot/docs/current/reference/html/howto.html#howto.data-initialization.migration-tool.flyway)
- [Expand-Contract Pattern](https://martinfowler.com/bliki/ParallelChange.html)

- [Presentation](https://docs.google.com/presentation/d/1z3l2eGlqNl8_RMLKt7Kjxi5WGsTWJUmCrlCokFuyz-0/edit?usp=sharing)

## Contributing

This is a training project. If you find issues or have suggestions for improvements:
1. Test your changes thoroughly
2. Ensure exercises still teach the intended concepts
3. Update documentation accordingly

## License

Internal Wise training material.

---

**Ready to learn?** Head over to [EXERCISES.md](EXERCISES.md) and start with Exercise 0!
