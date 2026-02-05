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
