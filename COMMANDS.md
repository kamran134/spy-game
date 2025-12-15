# Useful Commands for Spy Game Bot

## Docker Commands

### Start/Stop
```bash
# Start all containers
docker compose up -d

# Stop all containers
docker compose down

# Restart bot only
docker compose restart bot

# Restart all
docker compose restart
```

### Logs
```bash
# View bot logs (follow)
docker compose logs -f bot

# View all logs
docker compose logs -f

# View last 100 lines
docker compose logs --tail=100 bot
```

### Build
```bash
# Rebuild containers
docker compose build

# Rebuild without cache
docker compose build --no-cache

# Rebuild and start
docker compose up -d --build
```

## Database Commands

### Access PostgreSQL
```bash
# Connect to database
docker compose exec postgres psql -U postgres -d spy_game

# Inside psql:
\dt                    # List tables
\d users               # Describe users table
SELECT * FROM users;   # Query users
\q                     # Quit
```

### Database Operations
```bash
# Backup database
docker compose exec postgres pg_dump -U postgres spy_game > backup.sql

# Restore database
docker compose exec -T postgres psql -U postgres spy_game < backup.sql

# Reset database (DANGEROUS!)
docker compose down -v
docker compose up -d
```

## Bot Commands

### Run Scripts
```bash
# Populate locations
docker compose exec bot python scripts/populate_locations.py

# Run migrations
docker compose exec bot alembic upgrade head

# Create new migration
docker compose exec bot alembic revision --autogenerate -m "description"
```

### Python Shell
```bash
# Interactive Python shell in bot container
docker compose exec bot python

# In Python shell:
>>> from app.database.database import async_session_maker
>>> from app.database.repositories.user import UserRepository
>>> # ... your code
```

## Development Commands

### Local Development (without Docker)
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run bot
python -m app.main
```

### Code Quality
```bash
# Format code (if you install black)
pip install black
black app/

# Lint code (if you install pylint)
pip install pylint
pylint app/
```

## Monitoring

### Check Container Status
```bash
# List running containers
docker compose ps

# Check resource usage
docker stats

# Check container health
docker compose exec bot python -c "print('Bot is running!')"
```

### Check Bot Status
```bash
# Test database connection
docker compose exec bot python -c "
from app.database.database import async_session_maker
import asyncio

async def test():
    async with async_session_maker() as session:
        print('Database connection OK!')

asyncio.run(test())
"
```

## Troubleshooting

### Bot Not Starting
```bash
# Check logs
docker compose logs bot

# Check if port 5432 is available
netstat -an | grep 5432

# Restart everything
docker compose down
docker compose up -d
```

### Database Issues
```bash
# Check database logs
docker compose logs postgres

# Reset database
docker compose down
docker volume rm spy-game_postgres_data
docker compose up -d
```

### Permission Issues (Linux)
```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Fix Docker socket
sudo chmod 666 /var/run/docker.sock
```

## Production Commands

### Deploy
```bash
# On server
cd /root/spy-game
git pull origin main
docker compose down
docker compose build
docker compose up -d

# Check logs
docker compose logs -f bot
```

### Backup
```bash
# Backup database
docker compose exec postgres pg_dump -U postgres spy_game | gzip > backup_$(date +%Y%m%d).sql.gz

# Backup volumes
docker run --rm -v spy-game_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
```

### Monitoring
```bash
# Check disk usage
df -h

# Check memory
free -h

# Check running containers
docker ps

# Check bot uptime
docker compose exec bot python -c "import sys; print(sys.version)"
```

## Bot Game Commands

### Admin Commands (Group Only)
```
/startgame - Start player registration
/endregister - Start the game (after registration)
/next - Move to next player's turn
/endgame - End current game
/resumegame - Resume game (undo /endgame)
/settings - View/change game settings
/addlocation - Add new location
```

### Player Commands (Group)
```
/start - Register in the bot (in private chat first)
/help - Show help message
/vote @username - Vote for suspected spy (or reply to message)
/guess location - Spy guesses the location (fuzzy matching enabled)
```

### Game Features
- **Auto-next**: Reply to your turn message to automatically move to next player
- **Voting system**: All players vote, most voted player is revealed
- **Fuzzy guess**: Spy can make typos - 85%+ similarity accepted
- **Resume game**: Admin can undo accidental /endgame

### Example Game Flow
```
1. Admin: /startgame
2. Players: Click "Join" button
3. Admin: /endregister (when enough players)
4. Players: Receive roles in private
5. Players: Take turns naming associations (reply to auto-next)
6. Players: /vote @username when ready
7. Spy: /guess Hospital (can have typos like "Hosptal")
8. Game ends automatically after voting or guess
```

## Git Commands

### Common Workflow
```bash
# Check status
git status

# Add changes
git add .

# Commit
git commit -m "Description of changes"

# Push to GitHub
git push origin main

# Pull latest changes
git pull origin main
```

### Branches
```bash
# Create new branch
git checkout -b feature/new-feature

# Switch branch
git checkout main

# Merge branch
git merge feature/new-feature

# Delete branch
git branch -d feature/new-feature
```

## Quick Fixes

### "Port already in use"
```bash
# Find process using port 5432
lsof -i :5432  # Mac/Linux
netstat -ano | findstr :5432  # Windows

# Kill process
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows
```

### "Container name already in use"
```bash
docker rm -f spy_game_bot spy_game_db
docker compose up -d
```

### "No space left on device"
```bash
# Clean Docker
docker system prune -a --volumes

# Remove old images
docker image prune -a
```
