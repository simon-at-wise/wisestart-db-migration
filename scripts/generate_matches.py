#!/usr/bin/env python3
"""Generate 1 million match records directly via SQL inserts."""

import random
import requests
import sys
from datetime import datetime, timedelta
from pathlib import Path
from multiprocessing import Pool, cpu_count

# Configuration
NUM_MATCHES = 1_000_000
BATCH_SIZE = 1000  # Insert 1000 rows per INSERT statement
OUTPUT_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

API_BASE_URL = "http://localhost:8080"

def fetch_player_ids():
    """Fetch all player IDs from the API."""
    print("Fetching player IDs from API...")
    try:
        response = requests.get(f"{API_BASE_URL}/players", timeout=30)
        response.raise_for_status()
        players = response.json()

        if not players:
            print("❌ Error: No players found in the database")
            print("Please ensure the application is running and has player data")
            sys.exit(1)

        player_ids = [player['id'] for player in players]
        print(f"✓ Found {len(player_ids)} players (IDs: {min(player_ids)} - {max(player_ids)})")
        return player_ids
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API")
        print(f"Please ensure the application is running at {API_BASE_URL}")
        print("Start it with: ./gradlew bootRun")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching players: {e}")
        sys.exit(1)

def random_date(start_date, end_date):
    """Generate random datetime between start and end dates."""
    time_delta = end_date - start_date
    random_days = random.randint(0, time_delta.days)
    random_seconds = random.randint(0, 86400)
    return start_date + timedelta(days=random_days, seconds=random_seconds)

def generate_match_values(player_ids):
    """Generate a single match record values tuple."""
    player_id = random.choice(player_ids)
    score = random.randint(100, 10000)

    # Generate timestamps
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    played_at = random_date(start_date, end_date)

    # Difficulty - always provide a value
    difficulty = random.choice(['EASY', 'MEDIUM', 'HARD', 'EXPERT'])

    # time_started and time_ended - always provide
    match_duration_minutes = random.randint(5, 60)
    time_started = played_at - timedelta(minutes=match_duration_minutes)
    time_ended = played_at

    # settings JSON - always provide
    sound_enabled = random.choice([True, False])
    difficulty_modifier = round(random.uniform(0.5, 2.0), 1)
    settings = f'{{"sound": {str(sound_enabled).lower()}, "difficulty_modifier": {difficulty_modifier}}}'

    # max_level - always provide
    max_level = random.randint(1, 50)

    # experience_gained - always provide
    experience_gained = random.randint(50, 5000)

    # powerups JSON - always provide (random selection of powerups)
    available_powerups = ['shield', 'speed_boost', 'double_points', 'time_freeze', 'extra_life']
    num_powerups = random.randint(1, 3)
    selected_powerups = random.sample(available_powerups, num_powerups)
    powerups = '["' + '", "'.join(selected_powerups) + '"]'

    # feedback_score - always provide (1-5 rating)
    feedback_score = random.randint(1, 5)

    # Format values for SQL
    def sql_value(val):
        if val is None:
            return 'NULL'
        elif isinstance(val, str):
            # Escape single quotes
            escaped = val.replace("'", "''")
            return f"'{escaped}'"
        elif isinstance(val, datetime):
            return f"'{val.strftime('%Y-%m-%d %H:%M:%S')}'"
        else:
            return str(val)

    return f"({sql_value(player_id)}, {sql_value(score)}, {sql_value(played_at)}, " \
           f"{sql_value(difficulty)}, {sql_value(time_started)}, {sql_value(time_ended)}, " \
           f"{sql_value(settings)}, {sql_value(max_level)}, {sql_value(experience_gained)}, " \
           f"{sql_value(powerups)}, {sql_value(feedback_score)})"

def generate_batch(args):
    """Generate a single batch of SQL INSERT values (for multiprocessing)."""
    batch_num, batch_count, player_ids = args
    values = []
    for i in range(batch_count):
        values.append(generate_match_values(player_ids))
    return batch_num, values

def generate_matches_sql(player_ids):
    """Generate SQL file with match inserts using multiprocessing."""
    print(f"Generating SQL for {NUM_MATCHES:,} matches...")

    num_cpus = cpu_count()
    print(f"Using {num_cpus} CPU cores for parallel generation...")

    output_file = OUTPUT_DIR / "insert_matches.sql"
    num_batches = (NUM_MATCHES + BATCH_SIZE - 1) // BATCH_SIZE

    # Prepare batch arguments for multiprocessing
    batch_args = []
    for batch_num in range(num_batches):
        start_idx = batch_num * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, NUM_MATCHES)
        batch_count = end_idx - start_idx
        batch_args.append((batch_num, batch_count, player_ids))

    # Generate batches in parallel
    print("Generating match data in parallel...")
    with Pool(processes=num_cpus) as pool:
        results = []
        for i, result in enumerate(pool.imap(generate_batch, batch_args, chunksize=10)):
            results.append(result)
            if (i + 1) % 100 == 0:
                progress = ((i + 1) / num_batches) * 100
                print(f"  Progress: {i + 1}/{num_batches} batches ({progress:.1f}%)...")

    # Sort results by batch number to maintain order
    results.sort(key=lambda x: x[0])

    # Write to file
    print("Writing SQL file...")
    with open(output_file, 'w') as f:
        f.write("-- Generated match data inserts\n")
        f.write(f"-- Total matches: {NUM_MATCHES:,}\n")
        f.write(f"-- Player IDs: {len(player_ids)} players\n")
        f.write(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        for batch_num, values in results:
            batch_count = len(values)
            f.write(f"-- Batch {batch_num + 1}/{num_batches}: Inserting {batch_count} matches\n")
            f.write("INSERT INTO matches (player_id, score, played_at, difficulty, time_started, time_ended, settings, max_level, experience_gained, powerups, feedback_score)\nVALUES\n")
            f.write(",\n".join(values))
            f.write(";\n\n")

    print(f"✓ SQL file saved to {output_file}")
    print(f"  File size: {output_file.stat().st_size / (1024*1024):.1f} MB")

def main():
    print("=" * 60)
    print("Match Data SQL Generator")
    print("=" * 60)
    print()

    # Fetch player IDs from API
    player_ids = fetch_player_ids()

    print()
    print(f"Configuration:")
    print(f"  Total matches: {NUM_MATCHES:,}")
    print(f"  Batch size: {BATCH_SIZE:,} rows per INSERT")
    print(f"  Player count: {len(player_ids)}")
    print()

    generate_matches_sql(player_ids)

    print()
    print("=" * 60)
    print("✓ SQL generation complete!")
    print("=" * 60)
    print()
    print("To load the data, run:")
    print(f"  ./scripts/insert_match_data.sh")
    print()

if __name__ == "__main__":
    main()
