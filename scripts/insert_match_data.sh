#!/bin/bash

set -e

# Database connection details from application.yml
DB_HOST="localhost"
DB_PORT="3316"
DB_NAME="leaderboard"
DB_USER="leaderboard_user"
DB_PASS="leaderboard_pass"

# MySQL command (direct or via docker)
MYSQL_CMD="mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASS --skip-ssl $DB_NAME"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$PROJECT_ROOT/.venv"
DATA_DIR="$SCRIPT_DIR/../data"
SQL_FILE="$DATA_DIR/insert_matches.sql"

echo "=================================================="
echo "Match Data Insertion Script"
echo "=================================================="
echo ""

# Check for Python 3
echo "Checking for Python 3..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed."
    exit 1
fi
echo "✓ Python 3 found"
echo ""

# Generate the SQL file if it doesn't exist
if [ ! -f "$SQL_FILE" ]; then
    echo "SQL file not found. Generating match data..."
    echo ""

    # Create virtual environment if it doesn't exist
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating virtual environment at $VENV_DIR..."
        python3 -m venv "$VENV_DIR"
        echo "✓ Virtual environment created"
    else
        echo "✓ Virtual environment already exists"
    fi

    # Activate virtual environment
    echo "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"

    # Install/upgrade dependencies
    echo "Installing dependencies..."
    pip install --quiet --upgrade pip
    pip install --quiet requests
    echo "✓ Dependencies installed"
    echo ""

    # Run the Python script
    cd "$SCRIPT_DIR"
    python3 generate_matches.py

    # Deactivate virtual environment
    deactivate
    echo ""
fi

echo "Configuration:"
echo "  Database: $DB_NAME"
echo "  Host: $DB_HOST:$DB_PORT"
echo "  User: $DB_USER"
echo "  SQL File: $SQL_FILE"
echo ""

# Get file size
FILE_SIZE=$(du -h "$SQL_FILE" | cut -f1)
echo "SQL file size: $FILE_SIZE"
echo ""

# Check database connection
echo "Testing database connection..."
if $MYSQL_CMD -e "SELECT 1;" > /dev/null 2>&1; then
    echo "✓ Database connection successful"
else
    echo "❌ Error: Could not connect to database"
    echo ""
    echo "Make sure the database is running and accessible at $DB_HOST:$DB_PORT"
    echo ""
    exit 1
fi

echo ""
echo "Starting data insertion..."
echo "Will insert the SQL file 5 times (5 million total records)..."
echo ""

# Insert data 5 times
START_TIME=$(date +%s)
INSERT_ROUNDS=5

for round in $(seq 1 $INSERT_ROUNDS); do
    echo "=================================================="
    echo "Insertion round $round/$INSERT_ROUNDS"
    echo "=================================================="

    echo "Inserting with database optimizations..."
    echo "  - Disabling foreign key checks"
    echo "  - Disabling unique checks"
    echo "  - Disabling binary logging"
    echo "  - Using bulk insert buffer"
    echo ""

    # Create a temporary SQL file with optimizations
    TEMP_SQL=$(mktemp)
    cat > "$TEMP_SQL" << 'EOF'
-- Optimization settings for bulk insert
SET autocommit=0;
SET unique_checks=0;
SET foreign_key_checks=0;
SET sql_log_bin=0;

-- Increase bulk insert buffer
SET bulk_insert_buffer_size=256*1024*1024;

EOF

    # Append the actual data
    cat "$SQL_FILE" >> "$TEMP_SQL"

    # Append cleanup
    cat >> "$TEMP_SQL" << 'EOF'

-- Commit and restore settings
COMMIT;
SET unique_checks=1;
SET foreign_key_checks=1;
SET autocommit=1;
EOF

    ROUND_START=$(date +%s)
    $MYSQL_CMD < "$TEMP_SQL"
    ROUND_END=$(date +%s)
    ROUND_DURATION=$((ROUND_END - ROUND_START))

    # Clean up temp file
    rm "$TEMP_SQL"

    # Get current count
    CURRENT_COUNT=$($MYSQL_CMD -N -e "SELECT COUNT(*) FROM matches;")

    echo "✓ Round $round complete in ${ROUND_DURATION}s"
    echo "  Total matches: $CURRENT_COUNT"
    echo ""
done

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo "=================================================="
echo "✓ All data insertion complete!"
echo "=================================================="
echo "Total duration: ${DURATION}s"
echo ""

# Get final record count
FINAL_MATCH_COUNT=$($MYSQL_CMD -N -e "SELECT COUNT(*) FROM matches;")

echo "Total matches in database: $FINAL_MATCH_COUNT"
echo ""
