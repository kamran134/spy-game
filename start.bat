@echo off
REM Script to run the bot locally on Windows

echo Starting Spy Game Bot...

REM Check if .env exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Creating .env from .env.example...
    copy .env.example .env
    echo WARNING: Please edit .env file with your bot token and database password
    exit /b 1
)

REM Check if docker-compose.yml exists
if not exist docker-compose.yml (
    echo Creating docker-compose.yml from example...
    copy docker-compose.example.yml docker-compose.yml
)

REM Start containers
echo Starting containers...
docker compose up -d

REM Wait for database to be ready
echo Waiting for database...
timeout /t 5 /nobreak >nul

REM Populate default locations
echo Populating default locations...
docker compose exec bot python scripts/populate_locations.py

echo.
echo Bot is running!
echo.
echo Commands:
echo   docker compose logs -f bot     # View bot logs
echo   docker compose down            # Stop bot
echo   docker compose restart bot     # Restart bot

pause
