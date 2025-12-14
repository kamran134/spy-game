#!/bin/bash

# Script to run the bot locally

echo "Starting Spy Game Bot..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your bot token and database password"
    exit 1
fi

# Check if docker-compose.yml exists
if [ ! -f docker-compose.yml ]; then
    echo "Creating docker-compose.yml from example..."
    cp docker-compose.example.yml docker-compose.yml
fi

# Start containers
echo "Starting containers..."
docker compose up -d

# Wait for database to be ready
echo "Waiting for database..."
sleep 5

# Populate default locations
echo "Populating default locations..."
docker compose exec bot python scripts/populate_locations.py

echo "✅ Bot is running!"
echo ""
echo "Commands:"
echo "  docker compose logs -f bot     # View bot logs"
echo "  docker compose down            # Stop bot"
echo "  docker compose restart bot     # Restart bot"
