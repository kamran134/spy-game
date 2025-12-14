# 🎮 Spy Game Telegram Bot

<div align="center">

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![aiogram](https://img.shields.io/badge/aiogram-3.x-blue.svg)
![PostgreSQL](https://img.shields.io/badge/postgresql-15-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Многоязычный телеграм-бот для игры "Шпион"**

[Быстрый старт](#-быстрый-старт) •
[Возможности](#-возможности) •
[Документация](#-документация) •
[Деплой](#-деплой)

</div>

---

## 📖 О проекте

Spy Game Bot - это полнофункциональный телеграм-бот для популярной социальной игры "Шпион". Бот поддерживает несколько языков, настраиваемые параметры игры, кастомные локации и готов к продакшн деплою.

### Игра "Шпион"

В игре участвуют минимум 4 человека. Все игроки получают одну и ту же локацию, кроме одного - шпиона. Игроки по очереди называют ассоциации с этой локацией, пытаясь вычислить шпиона. Шпион же пытается угадать локацию по ассоциациям других игроков.

## ✨ Возможности

- 🎮 **Полноценная игра** - Регистрация, раздача ролей, система ходов
- 🌍 **Мультиязычность** - Русский, английский, азербайджанский
- 📍 **30+ локаций** - Готовый набор + возможность добавлять свои
- ⚙️ **Гибкие настройки** - Количество игроков, процент шпионов
- 👥 **Авто-регистрация** - Автоматическая регистрация при вступлении в группу
- 🎯 **Система очередности** - Автоматическая очередь игроков
- 🔒 **Приватность** - Роли отправляются в личные сообщения
- 🐳 **Docker-ready** - Запуск в один клик
- 🚀 **CI/CD** - Автоматический деплой через GitHub Actions

## 🚀 Быстрый старт

### 1️⃣ Получите токен
```
Telegram → @BotFather → /newbot → Сохраните токен
```

### 2️⃣ Настройте
```bash
cp .env.example .env
# Отредактируйте .env, вставьте BOT_TOKEN
```

### 3️⃣ Запустите
```bash
# Windows
start.bat

# Linux/Mac
chmod +x start.sh && ./start.sh

# Или вручную
docker compose up -d
```

### 4️⃣ Готово! 🎉
```
Telegram → Найдите бота → /start → Добавьте в группу → Играйте!
```

## 📚 Документация

- 📖 [QUICKSTART.md](QUICKSTART.md) - За 5 минут к игре
- 📘 [SETUP.md](SETUP.md) - Подробная инструкция по установке
- 📕 [COMMANDS.md](COMMANDS.md) - Все команды Docker, БД, Git
- 📗 [CHECKLIST.md](CHECKLIST.md) - Чеклист для деплоя на сервер
- 📙 [STRUCTURE.md](STRUCTURE.md) - Структура проекта
- 📓 [TODO.md](TODO.md) - Планы развития

## 🎯 Команды бота

### Для всех
```
/start  - Регистрация в системе
/help   - Помощь и правила
```

### Для админов
```
/settings [язык мин макс %]  - Настройки группы
/addlocation РУ | EN | AZ    - Добавить локацию
/startgame                   - Начать набор игроков
/endregister                 - Начать игру
/next                        - Следующий игрок
/endgame                     - Завершить игру
```

## 🏗️ Архитектура

```
┌─────────────────┐
│  Telegram API   │
└────────┬────────┘
         │
┌────────▼────────┐
│   Bot Handlers  │  (user, admin, game)
└────────┬────────┘
         │
┌────────▼────────┐
│  Repositories   │  (user, group, location, game)
└────────┬────────┘
         │
┌────────▼────────┐
│   PostgreSQL    │
└─────────────────┘
```

**Принципы:**
- Clean Architecture
- Repository Pattern
- Dependency Injection
- Async/Await
- Type Hints

## 📦 Технологии

| Компонент | Технология |
|-----------|-----------|
| Язык | Python 3.11 |
| Bot Framework | aiogram 3.x |
| База данных | PostgreSQL 15 |
| ORM | SQLAlchemy 2.0 |
| Миграции | Alembic |
| Контейнеризация | Docker & Docker Compose |
| CI/CD | GitHub Actions |

## 🚢 Деплой

### Локальный
```bash
docker compose up -d
```

### На сервер
1. Настройте GitHub Secrets (токены, SSH ключ)
2. Push в `main` ветку
3. GitHub Actions задеплоит автоматически

Подробнее: [CHECKLIST.md](CHECKLIST.md)

## 🤝 Участие в разработке

Мы приветствуем любой вклад! 

1. Fork репозитория
2. Создайте ветку: `git checkout -b feature/amazing-feature`
3. Commit изменений: `git commit -m 'Add amazing feature'`
4. Push в ветку: `git push origin feature/amazing-feature`
5. Откройте Pull Request

Читайте: [CONTRIBUTING.md](CONTRIBUTING.md)

## 📝 Roadmap

- [x] Базовая игровая механика
- [x] Мультиязычность (ru, en, az)
- [x] Docker деплой
- [x] CI/CD
- [ ] Голосование за шпиона
- [ ] Статистика игроков
- [ ] Дополнительные роли
- [ ] Таймер на ходы

Полный список: [TODO.md](TODO.md)

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. Подробности в [LICENSE](LICENSE).

## 🙏 Благодарности

- [aiogram](https://github.com/aiogram/aiogram) - Отличный фреймворк для Telegram ботов
- [SQLAlchemy](https://www.sqlalchemy.org/) - Мощная ORM для Python
- [PostgreSQL](https://www.postgresql.org/) - Надёжная база данных
- Сообщество Telegram Bot разработчиков

## 📞 Контакты

- 📫 Issues: [GitHub Issues](../../issues)
- 💬 Discussions: [GitHub Discussions](../../discussions)

## ⭐ Поддержите проект

Если вам нравится этот проект:
- ⭐ Поставьте звезду на GitHub
- 🐛 Сообщите о багах
- 💡 Предложите новые функции
- 🔀 Сделайте Pull Request

---

<div align="center">

**Создано с ❤️ для любителей игры "Шпион"**

</div>
