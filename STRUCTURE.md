# 📂 Project Structure

```
spy-game/
│
├── 📄 Core Files
│   ├── .env.example              # Environment variables template
│   ├── .gitignore                # Git ignore rules
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile                # Docker image config
│   ├── docker-compose.example.yml # Docker Compose template
│   ├── alembic.ini               # Alembic migrations config
│   ├── Makefile                  # Useful make commands
│   └── .editorconfig             # Editor configuration
│
├── 🚀 Quick Start Scripts
│   ├── start.sh                  # Linux/Mac startup script
│   └── start.bat                 # Windows startup script
│
├── 📚 Documentation
│   ├── README.md                 # Main project readme
│   ├── QUICKSTART.md             # 5-minute quick start guide
│   ├── SETUP.md                  # Complete setup instructions
│   ├── COMMANDS.md               # All Docker/DB/Git commands
│   ├── CHECKLIST.md              # Deployment checklist
│   ├── CONTRIBUTING.md           # Contribution guidelines
│   ├── CHANGELOG.md              # Version history
│   ├── PROJECT_SUMMARY.md        # Project overview
│   └── LICENSE                   # MIT license
│
├── 🤖 Application (app/)
│   ├── __init__.py
│   ├── main.py                   # Entry point, bot initialization
│   ├── config.py                 # Settings (Pydantic)
│   │
│   ├── 🎮 Bot Logic (bot/)
│   │   ├── __init__.py
│   │   │
│   │   ├── 🎯 Handlers (handlers/)
│   │   │   ├── __init__.py
│   │   │   ├── user.py           # /start, /help, registration
│   │   │   ├── admin.py          # /settings, /addlocation
│   │   │   └── game.py           # Game commands & mechanics
│   │   │
│   │   ├── ⌨️ Keyboards (keyboards/)
│   │   │   ├── __init__.py
│   │   │   ├── inline.py         # Inline keyboards
│   │   │   └── reply.py          # Reply keyboards (placeholder)
│   │   │
│   │   ├── 🔧 Middlewares (middlewares/)
│   │   │   ├── __init__.py
│   │   │   ├── database.py       # DB session injection
│   │   │   └── i18n.py           # Internationalization
│   │   │
│   │   ├── 🔍 Filters (filters/)
│   │   │   ├── __init__.py
│   │   │   └── admin.py          # Admin rights check
│   │   │
│   │   └── 🛠️ Utils (utils/)
│   │       ├── __init__.py
│   │       └── game_logic.py     # Game logic utilities
│   │
│   ├── 💾 Database (database/)
│   │   ├── __init__.py
│   │   ├── database.py           # SQLAlchemy connection
│   │   ├── models.py             # ORM models
│   │   │                         # - User
│   │   │                         # - Group
│   │   │                         # - Location
│   │   │                         # - Game
│   │   │                         # - GamePlayer
│   │   │
│   │   └── 📦 Repositories (repositories/)
│   │       ├── __init__.py
│   │       ├── user.py           # User CRUD operations
│   │       ├── group.py          # Group CRUD operations
│   │       ├── location.py       # Location CRUD operations
│   │       └── game.py           # Game CRUD operations
│   │
│   └── 🌍 Locales (locales/)
│       ├── ru.json               # Russian translations
│       ├── en.json               # English translations
│       └── az.json               # Azerbaijani translations
│
├── 🔄 Database Migrations (migrations/)
│   ├── env.py                    # Alembic environment
│   └── versions/
│       └── 001_initial.py        # Initial migration
│
├── 📜 Scripts (scripts/)
│   └── populate_locations.py    # Populate 30 default locations
│
├── 🚢 CI/CD (.github/)
│   └── workflows/
│       └── deploy.yml            # GitHub Actions deployment
│
└── 🔧 IDE Settings (.vscode/)
    ├── settings.json             # VS Code settings
    └── extensions.json           # Recommended extensions

```

## 📊 Key Metrics

- **Total Files:** ~40
- **Python Files:** ~20
- **Documentation Files:** 10
- **Configuration Files:** 10
- **Lines of Code:** ~2500+

## 🎯 Technology Stack

```
┌─────────────────────────────────────────┐
│           Telegram Bot API              │
│              (aiogram 3.x)              │
└─────────────────────────────────────────┘
                    │
                    ↓
┌─────────────────────────────────────────┐
│         Application Layer               │
│  - Handlers (user, admin, game)         │
│  - Middlewares (DB, i18n)               │
│  - Keyboards (inline buttons)           │
│  - Game Logic (spies, turns)            │
└─────────────────────────────────────────┘
                    │
                    ↓
┌─────────────────────────────────────────┐
│         Repository Layer                │
│  - UserRepository                       │
│  - GroupRepository                      │
│  - LocationRepository                   │
│  - GameRepository                       │
└─────────────────────────────────────────┘
                    │
                    ↓
┌─────────────────────────────────────────┐
│         Database Layer                  │
│      SQLAlchemy 2.0 (Async)             │
│         PostgreSQL 15                   │
└─────────────────────────────────────────┘
```

## 🔄 Data Flow

```
User → Telegram → Bot Handler → Middleware (i18n, DB)
                        ↓
                  Repository
                        ↓
                   Database
                        ↓
                  Repository
                        ↓
                  Response
                        ↓
                    User
```

## 🎮 Game Flow

```
/startgame (Admin)
      ↓
Registration Opens (Buttons: Join/Pass)
      ↓
Players Join
      ↓
/endregister (Admin)
      ↓
Game Starts (Random location, spies selected)
      ↓
Roles Revealed (Button: Reveal Role)
      ↓
Players Take Turns (/next by admin)
      ↓
Game Actions:
  - 🕵️ Spy reveals (guess location)
  - 🔍 Players accuse (voting)
      ↓
/endgame (Admin)
```

## 📦 Deployment Flow

```
Code Push to GitHub
      ↓
GitHub Actions Triggered
      ↓
SSH to Server
      ↓
Pull Latest Code
      ↓
Create .env from Secrets
      ↓
Docker Build
      ↓
Docker Compose Up
      ↓
Populate Locations
      ↓
Bot Running ✅
```

## 🎨 Architecture Principles

1. **Separation of Concerns**
   - Handlers → Business Logic
   - Repositories → Data Access
   - Models → Data Structure

2. **Dependency Injection**
   - Via Middlewares
   - Clean testable code

3. **Repository Pattern**
   - Abstract database operations
   - Easy to switch databases

4. **Internationalization**
   - JSON-based translations
   - Easy to add new languages

5. **Docker-First**
   - Consistent environments
   - Easy deployment

6. **CI/CD Ready**
   - Automated deployment
   - GitHub Actions integration
