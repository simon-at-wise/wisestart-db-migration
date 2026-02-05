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
