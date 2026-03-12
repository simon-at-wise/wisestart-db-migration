#!/usr/bin/env python3
"""
Script to load historical player data from CSV file into the leaderboard service.
Reads data/players_historical.csv and posts each player to the /players endpoint.
Uses multi-threading for faster processing.
"""

import csv
import requests
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# Configuration
API_BASE_URL = "http://localhost:8080"
PLAYERS_ENDPOINT = f"{API_BASE_URL}/players"
CSV_FILE_PATH = Path(__file__).parent.parent / "data" / "players_historical.csv"
NUM_THREADS = 10


def load_players_from_csv(csv_path):
    """Read players from CSV file and return as list of dicts."""
    players = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            players.append({
                'username': row['username'],
                'email': row['email']
            })
    return players


def create_player(username, email):
    """Create a single player via POST request."""
    payload = {
        'username': username,
        'email': email
    }

    try:
        response = requests.post(PLAYERS_ENDPOINT, json=payload, timeout=10)
        response.raise_for_status()
        return True, response.json()
    except requests.exceptions.RequestException as e:
        return False, str(e)


def process_player(player, progress_lock, counters, total_count):
    """Process a single player in a thread."""
    success, result = create_player(player['username'], player['email'])

    with progress_lock:
        if success:
            counters['success'] += 1
        else:
            counters['error'] += 1
            print(f"Error loading player: {player}")
            print(f"  Error details: {result}")

        counters['processed'] += 1
        if counters['processed'] % 100 == 0:
            print(f"Progress: {counters['processed']}/{total_count} players processed")

    return success, result


def main():
    """Main execution function."""
    if not CSV_FILE_PATH.exists():
        print(f"Error: CSV file not found at {CSV_FILE_PATH}")
        sys.exit(1)

    print(f"Loading players from {CSV_FILE_PATH}...")

    try:
        players = load_players_from_csv(CSV_FILE_PATH)
        print(f"Found {len(players)} players to load")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)

    # Check if API is accessible
    try:
        response = requests.get(f"{API_BASE_URL}/players", timeout=5)
        response.raise_for_status()
        print(f"API is accessible at {API_BASE_URL}")
    except requests.exceptions.RequestException as e:
        print(f"Error: Cannot connect to API at {API_BASE_URL}")
        print(f"Details: {e}")
        print("Make sure the application is running (./gradlew bootRun)")
        sys.exit(1)

    # Load players with multi-threading
    print(f"Using {NUM_THREADS} threads for parallel processing...")

    progress_lock = Lock()
    counters = {'success': 0, 'error': 0, 'processed': 0}

    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = [
            executor.submit(process_player, player, progress_lock, counters, len(players))
            for player in players
        ]

        # Wait for all tasks to complete
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                with progress_lock:
                    counters['error'] += 1
                print(f"Unexpected error: {e}")

    print("\n" + "=" * 50)
    print(f"Loading complete!")
    print(f"Successfully loaded: {counters['success']}")
    print(f"Errors: {counters['error']}")
    print(f"Total: {len(players)}")
    print("=" * 50)


if __name__ == "__main__":
    main()
