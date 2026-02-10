# Game Leaderboard Training Project Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Spring Boot training project with Flyway migrations to teach database migration best practices to new graduates at Wise.

**Architecture:** Standard Spring Boot application with JPA repositories, REST controllers, and Flyway migrations. MariaDB via Docker Compose. Includes data generation scripts, broken migrations for troubleshooting exercises, and comprehensive documentation.

**Tech Stack:** Spring Boot 3.x, Java 21, Flyway, MariaDB 11.2, Gradle, Docker Compose

---

## Task 1: Project Setup and Gradle Configuration

**Files:**
- Create: `settings.gradle`
- Create: `build.gradle`
- Create: `gradlew`, `gradlew.bat`, `gradle/wrapper/*`
- Create: `.gitignore`

**Step 1: Create settings.gradle**

```gradle
rootProject.name = 'game-leaderboard-service'
```

**Step 2: Create build.gradle**

```gradle
buildscript {
    dependencyLocking {
        lockAllConfigurations()
        lockMode = LockMode.STRICT
    }
}

plugins {
    id 'java'
    id 'org.springframework.boot' version '3.2.2'
    id 'io.spring.dependency-management' version '1.1.4'
}

java {
    sourceCompatibility = JavaVersion.VERSION_21
    targetCompatibility = JavaVersion.VERSION_21
}

group = 'com.wise'
version = '1.0.0-SNAPSHOT'

repositories {
    mavenCentral()
}

dependencies {
    // Spring Boot
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    implementation 'org.springframework.boot:spring-boot-starter-actuator'
    implementation 'org.springframework.boot:spring-boot-starter-validation'

    // Flyway
    implementation 'org.flywaydb:flyway-core'
    implementation 'org.flywaydb:flyway-mysql'

    // Database
    runtimeOnly 'org.mariadb.jdbc:mariadb-java-client'

    // Lombok
    compileOnly 'org.projectlombok:lombok'
    annotationProcessor 'org.projectlombok:lombok'

    // Testing
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}

test {
    useJUnitPlatform()
}
```

**Step 3: Initialize Gradle wrapper**

Run:
```bash
gradle wrapper --gradle-version 8.5
```

Expected: Gradle wrapper files created

**Step 4: Create .gitignore**

```
# Gradle
.gradle/
build/
!gradle/wrapper/gradle-wrapper.jar

# IDE
.idea/
*.iml
*.iws
*.ipr
out/

# Data
data/
*.csv

# OS
.DS_Store
```

**Step 5: Commit**

```bash
git add .
git commit -m "feat: initialize Spring Boot project with Gradle

Set up Java 21 Spring Boot project with Flyway and MariaDB dependencies.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Docker Compose Configuration

**Files:**
- Create: `docker-compose.yml`
- Create: `scripts/reset-database.sh`

**Step 1: Create docker-compose.yml**

```yaml
version: '3.8'

services:
  mariadb:
    image: mariadb:11.2
    container_name: leaderboard-db
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: leaderboard
      MYSQL_USER: leaderboard_user
      MYSQL_PASSWORD: leaderboard_pass
    ports:
      - "3306:3306"
    volumes:
      - mariadb-data:/var/lib/mysql
    command: --local-infile=1

volumes:
  mariadb-data:
```

**Step 2: Create scripts/reset-database.sh**

```bash
#!/bin/bash
set -e

echo "Stopping containers..."
docker-compose down -v

echo "Starting fresh database..."
docker-compose up -d

echo "Waiting for database to be ready..."
sleep 10

echo "Database reset complete!"
echo "You can now run: ./gradlew bootRun"
```

**Step 3: Make script executable**

Run:
```bash
chmod +x scripts/reset-database.sh
```

**Step 4: Test Docker Compose**

Run:
```bash
docker-compose up -d
docker-compose ps
```

Expected: mariadb container running on port 3306

**Step 5: Commit**

```bash
git add docker-compose.yml scripts/reset-database.sh
git commit -m "feat: add Docker Compose configuration for MariaDB

Include reset script for easy database cleanup during exercises.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Spring Boot Application Configuration

**Files:**
- Create: `src/main/resources/application.yml`
- Create: `src/main/java/com/wise/leaderboard/LeaderboardApplication.java`

**Step 1: Create application.yml**

```yaml
spring:
  application:
    name: game-leaderboard-service

  datasource:
    url: jdbc:mariadb://localhost:3306/leaderboard
    username: leaderboard_user
    password: leaderboard_pass
    driver-class-name: org.mariadb.jdbc.Driver

  jpa:
    hibernate:
      ddl-auto: validate
    show-sql: false
    properties:
      hibernate:
        dialect: org.hibernate.dialect.MariaDBDialect

  flyway:
    enabled: true
    baseline-on-migrate: true
    locations: classpath:db/migration
    url: jdbc:mariadb://localhost:3306/leaderboard
    user: leaderboard_user
    password: leaderboard_pass

server:
  port: 8080

management:
  endpoints:
    web:
      exposure:
        include: health,info
```

**Step 2: Create LeaderboardApplication.java**

```java
package com.wise.leaderboard;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class LeaderboardApplication {

    public static void main(String[] args) {
        SpringApplication.run(LeaderboardApplication.class, args);
    }
}
```

**Step 3: Test application startup**

Run:
```bash
./gradlew bootRun
```

Expected: Application starts but fails on missing migrations (expected at this stage)

**Step 4: Commit**

```bash
git add src/main/resources/application.yml src/main/java/com/wise/leaderboard/LeaderboardApplication.java
git commit -m "feat: configure Spring Boot application

Add database connection, JPA, and Flyway configuration.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Domain Models

**Files:**
- Create: `src/main/java/com/wise/leaderboard/model/Player.java`
- Create: `src/main/java/com/wise/leaderboard/model/Match.java`

**Step 1: Create Player.java**

```java
package com.wise.leaderboard.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "players")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Player {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank
    @Size(max = 50)
    @Column(nullable = false, unique = true, length = 50)
    private String username;

    @NotBlank
    @Email
    @Size(max = 100)
    @Column(nullable = false, unique = true, length = 100)
    private String email;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}
```

**Step 2: Create Match.java**

```java
package com.wise.leaderboard.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "matches")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Match {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotNull
    @Column(name = "player_id", nullable = false)
    private Long playerId;

    @NotNull
    @Column(nullable = false)
    private Integer score;

    @Column(name = "played_at", nullable = false)
    private LocalDateTime playedAt;

    @PrePersist
    protected void onCreate() {
        playedAt = LocalDateTime.now();
    }
}
```

**Step 3: Commit**

```bash
git add src/main/java/com/wise/leaderboard/model/
git commit -m "feat: add Player and Match domain models

Simple JPA entities for game leaderboard system.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 5: JPA Repositories

**Files:**
- Create: `src/main/java/com/wise/leaderboard/repository/PlayerRepository.java`
- Create: `src/main/java/com/wise/leaderboard/repository/MatchRepository.java`

**Step 1: Create PlayerRepository.java**

```java
package com.wise.leaderboard.repository;

import com.wise.leaderboard.model.Player;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface PlayerRepository extends JpaRepository<Player, Long> {

    Optional<Player> findByUsername(String username);

    Optional<Player> findByEmail(String email);
}
```

**Step 2: Create MatchRepository.java**

```java
package com.wise.leaderboard.repository;

import com.wise.leaderboard.model.Match;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface MatchRepository extends JpaRepository<Match, Long> {

    List<Match> findByPlayerIdOrderByPlayedAtDesc(Long playerId, Pageable pageable);

    @Query("SELECT m FROM Match m ORDER BY m.score DESC, m.playedAt DESC")
    List<Match> findTopScores(Pageable pageable);
}
```

**Step 3: Commit**

```bash
git add src/main/java/com/wise/leaderboard/repository/
git commit -m "feat: add JPA repositories

Add PlayerRepository and MatchRepository with basic queries.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 6: REST Controllers

**Files:**
- Create: `src/main/java/com/wise/leaderboard/controller/PlayerController.java`
- Create: `src/main/java/com/wise/leaderboard/controller/MatchController.java`
- Create: `src/main/java/com/wise/leaderboard/dto/CreatePlayerRequest.java`
- Create: `src/main/java/com/wise/leaderboard/dto/CreateMatchRequest.java`

**Step 1: Create CreatePlayerRequest.java**

```java
package com.wise.leaderboard.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

@Data
public class CreatePlayerRequest {

    @NotBlank(message = "Username is required")
    @Size(max = 50, message = "Username must be less than 50 characters")
    private String username;

    @NotBlank(message = "Email is required")
    @Email(message = "Email must be valid")
    @Size(max = 100, message = "Email must be less than 100 characters")
    private String email;
}
```

**Step 2: Create CreateMatchRequest.java**

```java
package com.wise.leaderboard.dto;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import lombok.Data;

@Data
public class CreateMatchRequest {

    @NotNull(message = "Player ID is required")
    private Long playerId;

    @NotNull(message = "Score is required")
    @Positive(message = "Score must be positive")
    private Integer score;
}
```

**Step 3: Create PlayerController.java**

```java
package com.wise.leaderboard.controller;

import com.wise.leaderboard.dto.CreatePlayerRequest;
import com.wise.leaderboard.model.Player;
import com.wise.leaderboard.repository.PlayerRepository;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/players")
public class PlayerController {

    private final PlayerRepository playerRepository;

    public PlayerController(PlayerRepository playerRepository) {
        this.playerRepository = playerRepository;
    }

    @GetMapping
    public List<Player> getAllPlayers() {
        return playerRepository.findAll();
    }

    @GetMapping("/{id}")
    public ResponseEntity<Player> getPlayerById(@PathVariable Long id) {
        return playerRepository.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<Player> createPlayer(@Valid @RequestBody CreatePlayerRequest request) {
        Player player = new Player();
        player.setUsername(request.getUsername());
        player.setEmail(request.getEmail());

        Player saved = playerRepository.save(player);
        return ResponseEntity.status(HttpStatus.CREATED).body(saved);
    }
}
```

**Step 4: Create MatchController.java**

```java
package com.wise.leaderboard.controller;

import com.wise.leaderboard.dto.CreateMatchRequest;
import com.wise.leaderboard.model.Match;
import com.wise.leaderboard.repository.MatchRepository;
import jakarta.validation.Valid;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/matches")
public class MatchController {

    private final MatchRepository matchRepository;

    public MatchController(MatchRepository matchRepository) {
        this.matchRepository = matchRepository;
    }

    @GetMapping
    public List<Match> getRecentMatches(@RequestParam(defaultValue = "20") int limit) {
        return matchRepository.findAll(PageRequest.of(0, limit)).getContent();
    }

    @GetMapping("/leaderboard")
    public List<Match> getLeaderboard(@RequestParam(defaultValue = "10") int limit) {
        return matchRepository.findTopScores(PageRequest.of(0, limit));
    }

    @PostMapping
    public ResponseEntity<Match> createMatch(@Valid @RequestBody CreateMatchRequest request) {
        Match match = new Match();
        match.setPlayerId(request.getPlayerId());
        match.setScore(request.getScore());

        Match saved = matchRepository.save(match);
        return ResponseEntity.status(HttpStatus.CREATED).body(saved);
    }
}
```

**Step 5: Commit**

```bash
git add src/main/java/com/wise/leaderboard/controller/ src/main/java/com/wise/leaderboard/dto/
git commit -m "feat: add REST controllers and DTOs

Simple endpoints for creating and listing players and matches.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 7: Initial Database Migrations (V1 and V2)

**Files:**
- Create: `src/main/resources/db/migration/V1__Initial_schema.sql`
- Create: `src/main/resources/db/migration/V2__Seed_initial_data.sql`

**Step 1: Create V1__Initial_schema.sql**

```sql
-- Create players table
CREATE TABLE players (
    id BIGINT NOT NULL AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_username (username),
    UNIQUE KEY uk_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create matches table
CREATE TABLE matches (
    id BIGINT NOT NULL AUTO_INCREMENT,
    player_id BIGINT NOT NULL,
    score INT NOT NULL,
    played_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_player_id (player_id),
    KEY idx_played_at (played_at),
    CONSTRAINT fk_matches_player FOREIGN KEY (player_id) REFERENCES players(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Step 2: Create V2__Seed_initial_data.sql**

```sql
-- Insert 10 initial players
INSERT INTO players (username, email, created_at) VALUES
('alice_gamer', 'alice@example.com', '2024-01-15 10:00:00'),
('bob_pro', 'bob@example.com', '2024-01-16 11:30:00'),
('charlie_plays', 'charlie@example.com', '2024-01-17 09:15:00'),
('diana_wins', 'diana@example.com', '2024-01-18 14:20:00'),
('eve_master', 'eve@example.com', '2024-01-19 16:45:00'),
('frank_ninja', 'frank@example.com', '2024-01-20 08:00:00'),
('grace_legend', 'grace@example.com', '2024-01-21 12:30:00'),
('hank_elite', 'hank@example.com', '2024-01-22 15:00:00'),
('iris_champ', 'iris@example.com', '2024-01-23 10:45:00'),
('jack_ace', 'jack@example.com', '2024-01-24 13:15:00');

-- Insert 20 match records
INSERT INTO matches (player_id, score, played_at) VALUES
(1, 1500, '2024-01-25 10:00:00'),
(2, 2300, '2024-01-25 10:15:00'),
(3, 1800, '2024-01-25 10:30:00'),
(4, 2100, '2024-01-25 10:45:00'),
(5, 2500, '2024-01-25 11:00:00'),
(1, 1700, '2024-01-25 11:15:00'),
(2, 2400, '2024-01-25 11:30:00'),
(3, 1900, '2024-01-25 11:45:00'),
(4, 2200, '2024-01-25 12:00:00'),
(5, 2600, '2024-01-25 12:15:00'),
(6, 1600, '2024-01-25 12:30:00'),
(7, 2000, '2024-01-25 12:45:00'),
(8, 2300, '2024-01-25 13:00:00'),
(9, 1400, '2024-01-25 13:15:00'),
(10, 1950, '2024-01-25 13:30:00'),
(6, 1750, '2024-01-25 13:45:00'),
(7, 2100, '2024-01-25 14:00:00'),
(8, 2450, '2024-01-25 14:15:00'),
(9, 1550, '2024-01-25 14:30:00'),
(10, 2050, '2024-01-25 14:45:00');
```

**Step 3: Test migrations**

Run:
```bash
./gradlew bootRun
```

Expected: Application starts successfully, migrations applied

**Step 4: Verify via REST API**

Run:
```bash
curl http://localhost:8080/players | jq
curl http://localhost:8080/matches/leaderboard | jq
```

Expected: 10 players, 20 matches returned

**Step 5: Commit**

```bash
git add src/main/resources/db/migration/
git commit -m "feat: add initial database migrations

V1: Create players and matches tables with proper indexes and constraints
V2: Seed with 10 players and 20 matches for baseline data

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 8: Data Generation Script

**Files:**
- Create: `scripts/generate-data.sh`
- Create: `scripts/generate-data.py`

**Step 1: Create generate-data.py**

```python
#!/usr/bin/env python3
"""Generate large CSV datasets for database migration exercises."""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
NUM_PLAYERS = 100_000
NUM_MATCHES = 500_000
NUM_BATCH2_MATCHES = 50_000
DUPLICATE_PERCENTAGE = 0.1  # 10% duplicates in batch2

OUTPUT_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

def random_date(start_date, end_date):
    """Generate random datetime between start and end dates."""
    time_delta = end_date - start_date
    random_days = random.randint(0, time_delta.days)
    random_seconds = random.randint(0, 86400)
    return start_date + timedelta(days=random_days, seconds=random_seconds)

def generate_players():
    """Generate players CSV."""
    print(f"Generating {NUM_PLAYERS:,} players...")

    adjectives = ["swift", "mighty", "clever", "brave", "silent", "fierce", "wise", "dark", "bright", "cool"]
    nouns = ["dragon", "phoenix", "tiger", "wolf", "eagle", "ninja", "warrior", "mage", "knight", "hunter"]

    players_file = OUTPUT_DIR / "players_historical.csv"

    with open(players_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['username', 'email', 'created_at'])

        start_date = datetime(2023, 1, 1)
        end_date = datetime(2024, 1, 1)

        for i in range(NUM_PLAYERS):
            adj = random.choice(adjectives)
            noun = random.choice(nouns)
            username = f"{adj}_{noun}_{i}"
            email = f"{username}@gamers.example.com"
            created_at = random_date(start_date, end_date).strftime('%Y-%m-%d %H:%M:%S')

            writer.writerow([username, email, created_at])

            if (i + 1) % 10000 == 0:
                print(f"  Generated {i + 1:,} players...")

    print(f"✓ Players saved to {players_file}")

def generate_matches():
    """Generate matches CSV."""
    print(f"Generating {NUM_MATCHES:,} matches...")

    matches_file = OUTPUT_DIR / "matches_historical.csv"

    with open(matches_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['player_id', 'score', 'played_at'])

        start_date = datetime(2023, 1, 1)
        end_date = datetime(2024, 1, 1)

        # Existing players are IDs 1-10, historical players start at 11
        player_id_start = 11
        player_id_end = player_id_start + NUM_PLAYERS - 1

        for i in range(NUM_MATCHES):
            player_id = random.randint(player_id_start, player_id_end)
            score = random.randint(100, 5000)
            played_at = random_date(start_date, end_date).strftime('%Y-%m-%d %H:%M:%S')

            writer.writerow([player_id, score, played_at])

            if (i + 1) % 50000 == 0:
                print(f"  Generated {i + 1:,} matches...")

    print(f"✓ Matches saved to {matches_file}")

def generate_batch2_with_duplicates():
    """Generate batch2 matches with some duplicates from original matches."""
    print(f"Generating {NUM_BATCH2_MATCHES:,} batch2 matches (with {DUPLICATE_PERCENTAGE*100:.0f}% duplicates)...")

    # Read some existing matches to duplicate
    matches_file = OUTPUT_DIR / "matches_historical.csv"
    existing_matches = []

    with open(matches_file, 'r') as f:
        reader = csv.DictReader(f)
        existing_matches = list(reader)[:1000]  # Take first 1000 for duplicates

    batch2_file = OUTPUT_DIR / "matches_batch2.csv"

    with open(batch2_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['player_id', 'score', 'played_at'])

        num_duplicates = int(NUM_BATCH2_MATCHES * DUPLICATE_PERCENTAGE)
        num_new = NUM_BATCH2_MATCHES - num_duplicates

        start_date = datetime(2023, 6, 1)
        end_date = datetime(2024, 1, 1)

        # Write new matches
        player_id_start = 11
        player_id_end = player_id_start + NUM_PLAYERS - 1

        for i in range(num_new):
            player_id = random.randint(player_id_start, player_id_end)
            score = random.randint(100, 5000)
            played_at = random_date(start_date, end_date).strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([player_id, score, played_at])

        # Write duplicate matches
        for i in range(num_duplicates):
            match = random.choice(existing_matches)
            writer.writerow([match['player_id'], match['score'], match['played_at']])

    print(f"✓ Batch2 matches saved to {batch2_file}")
    print(f"  ({num_new:,} new matches, {num_duplicates:,} duplicates)")

def main():
    print("=" * 60)
    print("Game Leaderboard - Data Generation")
    print("=" * 60)
    print()

    generate_players()
    generate_matches()
    generate_batch2_with_duplicates()

    print()
    print("=" * 60)
    print("✓ All data generated successfully!")
    print("=" * 60)
    print()
    print("Files created:")
    print(f"  - {OUTPUT_DIR}/players_historical.csv ({NUM_PLAYERS:,} rows)")
    print(f"  - {OUTPUT_DIR}/matches_historical.csv ({NUM_MATCHES:,} rows)")
    print(f"  - {OUTPUT_DIR}/matches_batch2.csv ({NUM_BATCH2_MATCHES:,} rows)")
    print()

if __name__ == "__main__":
    main()
```

**Step 2: Create generate-data.sh wrapper**

```bash
#!/bin/bash
set -e

echo "Checking for Python 3..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

python3 generate-data.py

echo ""
echo "Data generation complete!"
echo "CSV files are ready in the data/ directory."
```

**Step 3: Make scripts executable**

Run:
```bash
chmod +x scripts/generate-data.sh scripts/generate-data.py
```

**Step 4: Test data generation**

Run:
```bash
./scripts/generate-data.sh
```

Expected: CSV files created in data/ directory

**Step 5: Commit**

```bash
git add scripts/generate-data.sh scripts/generate-data.py
git commit -m "feat: add data generation scripts

Python script to generate 100k players, 500k matches, and batch2 with duplicates.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 9: Broken Migrations for Exercises

**Files:**
- Create: `broken-migrations/README.md`
- Create: `broken-migrations/V6__add_achievements_BROKEN.sql`
- Create: `broken-migrations/V8__add_region_NOT_NULL.sql`
- Create: `broken-migrations/V10__load_match_batch2.sql`

**Step 1: Create broken-migrations/README.md**

```markdown
# Broken Migrations

These migrations are intentionally broken for training exercises.
Do NOT copy them directly - they are designed to fail and teach recovery techniques.

## Exercise Files

- `V6__add_achievements_BROKEN.sql` - Exercise 5: Failed migration midway
- `V8__add_region_NOT_NULL.sql` - Exercise 7: Adding NOT NULL without backfill
- `V10__load_match_batch2.sql` - Exercise 9: Duplicate key violations

Refer to EXERCISES.md for instructions on when and how to use each file.
```

**Step 2: Create V6__add_achievements_BROKEN.sql**

```sql
-- Exercise 5: This migration will fail midway through
-- Used to teach recovery from partially applied migrations

-- This succeeds
CREATE TABLE achievements (
    id BIGINT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    points INT NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- This fails - missing closing quote on string value
INSERT INTO achievements (name, description, points) VALUES
('First Win', 'Win your first match', 10),
('Winning Streak', 'Win 5 matches in a row', 50),
('High Scorer', 'Score over 5000 points, 100);
-- Syntax error above: missing closing quote before 100

-- This never executes because migration fails before reaching it
CREATE TABLE player_achievements (
    player_id BIGINT NOT NULL,
    achievement_id BIGINT NOT NULL,
    earned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (player_id, achievement_id),
    CONSTRAINT fk_player_achievements_player FOREIGN KEY (player_id) REFERENCES players(id),
    CONSTRAINT fk_player_achievements_achievement FOREIGN KEY (achievement_id) REFERENCES achievements(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Step 3: Create V8__add_region_NOT_NULL.sql**

```sql
-- Exercise 7: This migration will fail on existing data
-- Used to teach the proper multi-step approach for adding NOT NULL constraints

-- WRONG: Trying to add NOT NULL column to table with existing data
ALTER TABLE players ADD COLUMN region VARCHAR(50) NOT NULL;

-- This fails because existing players have NULL for region
-- Proper approach would be:
-- 1. Add column as nullable
-- 2. Backfill data
-- 3. Add NOT NULL constraint
```

**Step 4: Create V10__load_match_batch2.sql**

```sql
-- Exercise 9: This migration may cause duplicate key violations
-- Used to teach idempotency patterns

-- This will fail if we add a unique constraint on (player_id, score, played_at)
-- or create duplicates if we don't have that constraint

LOAD DATA LOCAL INFILE '../../data/matches_batch2.csv'
INTO TABLE matches
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(player_id, score, @played_at)
SET played_at = STR_TO_DATE(@played_at, '%Y-%m-%d %H:%i:%s');

-- Issues:
-- 1. LOAD DATA LOCAL INFILE requires local_infile=1 (already set in docker-compose)
-- 2. File path may need adjustment
-- 3. No handling of duplicates
-- 4. Not idempotent - running twice creates duplicates

-- Students should learn about:
-- - INSERT IGNORE
-- - ON DUPLICATE KEY UPDATE
-- - Adding unique constraints
-- - Making migrations idempotent
```

**Step 5: Commit**

```bash
git add broken-migrations/
git commit -m "feat: add broken migrations for exercises

Intentionally broken migrations for teaching recovery and troubleshooting.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 10: Exercise Documentation

**Files:**
- Create: `EXERCISES.md`

**Step 1: Create EXERCISES.md**

```markdown
# Database Migration Exercises

Work through these exercises in teams of 3-4 people. The documentation is intentionally light - discuss approaches with your team and ask instructors if you get stuck.

## Prerequisites

- Java 21 installed
- Docker and Docker Compose installed
- Basic SQL knowledge

## Exercise 0: Setup (5 minutes)

**Goal:** Get the application running and verify the baseline setup.

**Instructions:**
1. Start the database: `docker-compose up -d`
2. Start the application: `./gradlew bootRun`
3. Verify it's working:
   - `curl http://localhost:8080/players`
   - `curl http://localhost:8080/matches`
4. Connect to the database and explore the `flyway_schema_history` table

**Discussion:**
- What information does Flyway track in `flyway_schema_history`?
- Why is the `checksum` column important?

---

## Exercise 1: Backfill Historical Data (15 minutes)

**Goal:** Load large amounts of historical data efficiently.

**Context:** Marketing found historical game data from 2023 that needs to be imported into our system.

**Instructions:**
1. Generate the CSV files: `./scripts/generate-data.sh`
2. Create a V3 migration to load the data from:
   - `data/players_historical.csv`
   - `data/matches_historical.csv`
3. Run the migration and observe how long it takes

**Discussion:**
- What approaches can you use to load CSV data? (LOAD DATA INFILE vs batched INSERTs)
- How long did your migration take?
- What happens if the migration times out?
- How can you adjust Flyway timeout settings?

**Hint:** You may need to use `LOAD DATA LOCAL INFILE` and handle the file paths carefully.

---

## Exercise 2: Adding Safe Columns (5 minutes)

**Goal:** Understand what makes a schema change "safe".

**Context:** Product wants to track which country players are from and what game mode was played in each match.

**Instructions:**
1. Create V4 migration to add nullable `country` column (VARCHAR 2) to players table
2. Create V5 migration to add nullable `game_mode` column (VARCHAR 20) to matches table
3. Run the migrations

**Discussion:**
- Why is adding a nullable column safe?
- What would happen if we added these as NOT NULL?
- Does this block writes to the table?

---

## Exercise 3: Adding Indexes - Table Locking (10 minutes)

**Goal:** Experience table locking with large datasets.

**Context:** The leaderboard page is slow. We need an index on `matches.score` to improve query performance.

**Instructions:**
1. First, query the matches table to see its size: `SELECT COUNT(*) FROM matches;`
2. Create V6 migration to add an index on `matches.score`
3. Run the migration and time how long it takes
4. Try to query the matches table while the migration is running (in another terminal)

**Discussion:**
- How long did the index creation take?
- Could you query the table during index creation?
- In production, what would this mean for your application?
- Research: What is `ALGORITHM=INPLACE` vs `ALGORITHM=COPY` in MySQL?

---

## Exercise 4: Checksum Mismatch Recovery (10 minutes)

**Goal:** Recover from an edited migration file.

**Context:** A teammate "fixed" a typo in one of your applied migrations by editing the file directly.

**Instructions:**
1. Make sure your application is running successfully
2. Edit the V2 migration file (change a comment or add whitespace)
3. Stop and restart the application
4. Observe what happens
5. Fix the problem

**Discussion:**
- Why did Flyway reject the change?
- What is the correct way to fix a mistake in an applied migration?
- When is it safe to edit a migration file?

**Hint:** Look into `flyway repair` command.

---

## Exercise 5: Failed Migration Recovery (15 minutes)

**Goal:** Recover from a migration that failed partway through.

**Context:** A teammate wrote a migration to add an achievements system, but it's failing.

**Instructions:**
1. Copy `broken-migrations/V6__add_achievements_BROKEN.sql` to your migrations folder (rename to remove _BROKEN)
2. Try to start the application
3. Investigate what went wrong:
   - What tables exist in the database?
   - What does `flyway_schema_history` say?
4. Fix the migration and get the application running

**Discussion:**
- What state is the database in after a failed migration?
- Why did some tables get created but not others?
- What's the recovery process?
- How can you prevent this type of failure?

---

## Exercise 6: Column Type Change - Locking Impact (10 minutes)

**Goal:** Experience table locking during column modifications.

**Context:** Product wants to support scores higher than 2 billion. We need to change `matches.score` from INT to BIGINT.

**Instructions:**
1. Create V7 migration: `ALTER TABLE matches MODIFY COLUMN score BIGINT NOT NULL;`
2. Before running, estimate: how long will this take?
3. Run the migration and time it
4. Try to insert a new match while the migration runs

**Discussion:**
- How long did it take compared to adding an index?
- Could you write to the table during the migration?
- In production, how would you handle this type of change?
- Research: What is the "expand-contract" pattern?

---

## Exercise 7: Adding NOT NULL Without Backfill (15 minutes)

**Goal:** Learn the proper multi-step approach for constraints.

**Context:** Product decided that all players must have a region. It's a required field.

**Instructions:**
1. Copy `broken-migrations/V8__add_region_NOT_NULL.sql` to your migrations folder
2. Try to run the application
3. Investigate what went wrong
4. Fix the issue using a proper multi-step approach

**Discussion:**
- Why did the migration fail?
- What's the correct sequence of steps?
- What state is your database in now?
- How do you recover?

**Hint:** The proper pattern is: add nullable → backfill data → add constraint.

---

## Exercise 8: Renaming Columns - Breaking Changes (10 minutes)

**Goal:** Understand coordination between schema and code changes.

**Context:** The team decided `username` should be called `player_name` for consistency.

**Instructions:**
1. Create V9 migration: `ALTER TABLE players CHANGE COLUMN username player_name VARCHAR(50) NOT NULL;`
2. Run the migration (it succeeds!)
3. Try to use the application - create a new player via the API
4. Observe what breaks

**Discussion:**
- Why does the application fail even though the migration succeeded?
- How should schema changes be coordinated with code changes?
- What is the "expand-contract" pattern for zero-downtime deploys?
- How would you do this rename safely in production?

**Recovery:** Roll back the migration or update the Java code to match.

---

## Exercise 9: Duplicate Keys and Idempotency (15 minutes)

**Goal:** Learn idempotency patterns for data migrations.

**Context:** We found another batch of historical match data that needs importing. Some records might overlap with existing data.

**Instructions:**
1. The file `data/matches_batch2.csv` contains ~50k matches, some are duplicates
2. Copy `broken-migrations/V10__load_match_batch2.sql` to your migrations folder
3. Decide: should match data allow duplicates or not?
4. Try to run the migration - what happens?
5. Fix it using proper idempotency patterns

**Discussion:**
- Should matches be unique by (player_id, score, played_at)?
- What are the options for handling duplicates?
  - `INSERT IGNORE`
  - `ON DUPLICATE KEY UPDATE`
  - `REPLACE INTO`
- Which approach is right for match data?
- How do you make migrations idempotent (safe to re-run)?

---

## Useful Commands

**Reset everything:**
```bash
./scripts/reset-database.sh
./gradlew clean bootRun
```

**Check Flyway status:**
```bash
./gradlew flywayInfo
```

**Repair Flyway checksums:**
```bash
./gradlew flywayRepair
```

**Connect to database:**
```bash
docker exec -it leaderboard-db mysql -u leaderboard_user -pleaderboard_pass leaderboard
```

**Check migration history:**
```sql
SELECT * FROM flyway_schema_history ORDER BY installed_rank;
```

**Check table locks:**
```sql
SHOW OPEN TABLES WHERE In_use > 0;
```

---

## Common Pitfalls

1. **Editing applied migrations** - Never edit a migration that's been applied. Create a new one.
2. **Forgetting to backfill** - Add nullable, backfill data, then add constraint.
3. **Large table changes** - Be aware of locking and execution time on tables with millions of rows.
4. **Non-idempotent data migrations** - Always handle duplicates and make migrations re-runnable.
5. **Not testing locally first** - Always run migrations locally before production.

---

## Production Best Practices

1. **Estimate execution time** - Know how long your migration will take
2. **Understand locking** - Know which operations lock tables
3. **Test with production-like data volumes** - 10 rows behave differently than 10 million
4. **Make migrations atomic** - Keep them small and focused
5. **Handle failures gracefully** - Plan for rollback or manual intervention
6. **Use expand-contract for breaking changes** - Add new, migrate code, remove old
7. **Monitor during deployment** - Watch for locks, slow queries, errors

---

Good luck! Remember: breaking things and fixing them is the best way to learn. Ask instructors if you get stuck.
```

**Step 2: Commit**

```bash
git add EXERCISES.md
git commit -m "docs: add exercise instructions

Light documentation for 9 hands-on database migration exercises.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 11: Solutions Documentation (Instructor Guide)

**Files:**
- Create: `SOLUTIONS.md`

**Step 1: Create SOLUTIONS.md**

Due to length, this file contains complete solutions for all exercises. See the content below.

```markdown
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
```

**Step 2: Commit**

```bash
git add SOLUTIONS.md
git commit -m "docs: add instructor solutions guide

Complete solutions, explanations, and teaching notes for all exercises.
Extract this file before sharing with students.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 12: README Documentation

**Files:**
- Create: `README.md`

**Step 1: Create README.md**

```markdown
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
- **Git** - For version control

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd game-leaderboard-service
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

# Check migration history
curl http://localhost:8080/actuator/health
```

### 5. Explore Database

```bash
docker exec -it leaderboard-db mysql -u leaderboard_user -pleaderboard_pass leaderboard
```

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
game-leaderboard-service/
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

### Database

```bash
# Start database
docker-compose up -d

# Stop database
docker-compose down

# Reset everything (nuclear option)
./scripts/reset-database.sh

# Connect to database
docker exec -it leaderboard-db mysql -u leaderboard_user -pleaderboard_pass leaderboard

# View logs
docker-compose logs -f mariadb
```

### Flyway

```bash
# Show migration status
./gradlew flywayInfo

# Repair checksums
./gradlew flywayRepair

# Validate migrations
./gradlew flywayValidate
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
    "email": "player@example.com"
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
    "score": 2500
  }
  ```

### Health

- `GET /actuator/health` - Application health status

## Database Schema

### `players` Table

| Column      | Type          | Constraints          |
|-------------|---------------|----------------------|
| id          | BIGINT        | PRIMARY KEY, AUTO_INCREMENT |
| username    | VARCHAR(50)   | UNIQUE, NOT NULL     |
| email       | VARCHAR(100)  | UNIQUE, NOT NULL     |
| created_at  | TIMESTAMP     | NOT NULL             |

### `matches` Table

| Column      | Type          | Constraints                    |
|-------------|---------------|--------------------------------|
| id          | BIGINT        | PRIMARY KEY, AUTO_INCREMENT    |
| player_id   | BIGINT        | NOT NULL, FOREIGN KEY → players.id |
| score       | INT           | NOT NULL                       |
| played_at   | TIMESTAMP     | NOT NULL                       |

**Indexes:**
- `idx_player_id` on player_id
- `idx_played_at` on played_at

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
```bash
# Check database is running
docker-compose ps

# If not running
docker-compose up -d

# Wait 10 seconds, then retry
./gradlew bootRun
```

### Port 3306 already in use

**Symptom:** "Port 3306 is already allocated"

**Solution:**
```bash
# Stop local MySQL/MariaDB
sudo systemctl stop mysql  # Linux
brew services stop mariadb  # macOS

# Or change port in docker-compose.yml and application.yml
ports:
  - "3307:3306"  # Map to 3307 instead
```

### Migration checksum mismatch

**Symptom:** "Migration checksum mismatch for migration version X"

**Solution:**
```bash
# See which migration has mismatch
./gradlew flywayInfo

# If you edited a migration file, revert it
git checkout -- src/main/resources/db/migration/VX__*.sql

# Repair checksums
./gradlew flywayRepair

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
./gradlew flywayRepair

# Restart (will re-run the migration)
./gradlew bootRun
```

### Need to start over

**Symptom:** Database is in unknown state

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
5. **File paths in LOAD DATA** - Use absolute paths or mount volumes correctly.

## Learning Resources

- [Flyway Documentation](https://flywaydb.org/documentation/)
- [MySQL Online DDL](https://dev.mysql.com/doc/refman/8.0/en/innodb-online-ddl.html)
- [Spring Boot + Flyway](https://docs.spring.io/spring-boot/docs/current/reference/html/howto.html#howto.data-initialization.migration-tool.flyway)
- [Expand-Contract Pattern](https://martinfowler.com/bliki/ParallelChange.html)

## Contributing

This is a training project. If you find issues or have suggestions for improvements:
1. Test your changes thoroughly
2. Ensure exercises still teach the intended concepts
3. Update documentation accordingly

## License

Internal Wise training material.

---

**Ready to learn?** Head over to [EXERCISES.md](EXERCISES.md) and start with Exercise 0!
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add comprehensive README

Quick start guide, API documentation, troubleshooting, and project overview.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 13: Basic Test

**Files:**
- Create: `src/test/java/com/wise/leaderboard/LeaderboardApplicationTests.java`

**Step 1: Create basic test**

```java
package com.wise.leaderboard;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

@SpringBootTest
@ActiveProfiles("test")
class LeaderboardApplicationTests {

    @Test
    void contextLoads() {
        // Test that Spring context loads successfully
    }
}
```

**Step 2: Create test profile**

Create `src/test/resources/application-test.yml`:

```yaml
spring:
  datasource:
    url: jdbc:mariadb://localhost:3306/leaderboard
    username: leaderboard_user
    password: leaderboard_pass

  jpa:
    show-sql: false

  flyway:
    enabled: true
    clean-disabled: false
```

**Step 3: Run test**

Run:
```bash
./gradlew test
```

Expected: Test passes

**Step 4: Commit**

```bash
git add src/test/
git commit -m "test: add basic application context test

Verify Spring Boot application starts successfully.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 14: Final Polish and Validation

**Files:**
- Review all files
- Test complete workflow
- Create final git tag

**Step 1: Full integration test**

Run complete workflow:
```bash
# Reset everything
./scripts/reset-database.sh

# Generate data
./scripts/generate-data.sh

# Start application
./gradlew clean bootRun
```

Expected: Application starts, V1 and V2 applied, data generation works

**Step 2: Test REST API**

```bash
curl http://localhost:8080/players | jq
curl http://localhost:8080/matches/leaderboard | jq
```

Expected: 10 players, 20 matches returned

**Step 3: Verify Docker**

```bash
docker-compose ps
docker exec -it leaderboard-db mysql -u leaderboard_user -pleaderboard_pass leaderboard -e "SELECT COUNT(*) FROM players;"
```

Expected: 10 rows

**Step 4: Tag release**

```bash
git tag -a v1.0.0 -m "Initial release of game leaderboard training project"
```

**Step 5: Final commit**

```bash
git add .
git commit -m "chore: final polish and validation

Complete game leaderboard training project ready for use.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>" --allow-empty
```

---

## Execution Summary

This plan creates a complete Spring Boot training project with:

- ✅ Working application with REST API
- ✅ Docker Compose database setup
- ✅ Initial Flyway migrations (V1, V2)
- ✅ Data generation scripts (100k+ rows)
- ✅ Broken migrations for troubleshooting exercises
- ✅ Comprehensive exercise documentation
- ✅ Complete instructor solutions guide
- ✅ Professional README

**Total tasks:** 14
**Estimated time:** 4-6 hours for full implementation
**Files created:** ~30 files

All exercises teach production-relevant concepts through hands-on troubleshooting.
