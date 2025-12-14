# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-01

### Added
- Initial release
- Core game mechanics (Spy game)
- Multi-language support (Russian, English, Azerbaijani)
- Group settings management
- Custom locations per group
- Auto-registration on group join
- Player turn system
- Default 30+ locations
- Docker deployment support
- GitHub Actions CI/CD
- Admin commands for game management
- User registration system
- Database with PostgreSQL
- SQLAlchemy models and repositories
- Alembic migrations
- Comprehensive documentation

### Features
- `/start` - User registration
- `/help` - Help and rules
- `/settings` - Configure group settings
- `/addlocation` - Add custom locations
- `/startgame` - Start player registration
- `/endregister` - Begin game
- `/next` - Move to next player
- `/endgame` - End current game
- Role reveal buttons
- Private message support for roles
- Configurable min/max players
- Configurable spy percentage

## [Unreleased]

### Planned
- Voting mechanism for spy accusations
- Player statistics
- Optional timer for turns
- Additional roles (besides spy)
- Admin panel for location management
- Location export/import between groups
- Game history
- Leaderboards
