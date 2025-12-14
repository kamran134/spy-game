.PHONY: help start stop restart logs build clean test

help:
	@echo "Spy Game Bot - Available commands:"
	@echo ""
	@echo "  make start       - Start all containers"
	@echo "  make stop        - Stop all containers"
	@echo "  make restart     - Restart bot container"
	@echo "  make logs        - Show bot logs"
	@echo "  make build       - Rebuild containers"
	@echo "  make clean       - Remove all containers and volumes"
	@echo "  make populate    - Populate default locations"
	@echo "  make backup      - Backup database"
	@echo "  make shell       - Open bot container shell"
	@echo "  make db          - Open PostgreSQL shell"

start:
	@echo "Starting containers..."
	docker compose up -d
	@echo "✅ Containers started!"

stop:
	@echo "Stopping containers..."
	docker compose down
	@echo "✅ Containers stopped!"

restart:
	@echo "Restarting bot..."
	docker compose restart bot
	@echo "✅ Bot restarted!"

logs:
	docker compose logs -f bot

build:
	@echo "Building containers..."
	docker compose build --no-cache
	docker compose up -d
	@echo "✅ Containers rebuilt!"

clean:
	@echo "⚠️  This will remove all containers and volumes!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker compose down -v; \
		echo "✅ Cleaned!"; \
	fi

populate:
	@echo "Populating default locations..."
	docker compose exec bot python scripts/populate_locations.py
	@echo "✅ Locations populated!"

backup:
	@echo "Creating database backup..."
	docker compose exec postgres pg_dump -U postgres spy_game | gzip > backup_$$(date +%Y%m%d_%H%M%S).sql.gz
	@echo "✅ Backup created!"

shell:
	docker compose exec bot /bin/bash

db:
	docker compose exec postgres psql -U postgres -d spy_game
