from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.DEBUG,
    future=True
)

# Create session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    async with async_session_maker() as session:
        yield session


async def init_db():
    """Initialize database"""
    async with engine.begin() as conn:
        # Import all models here to ensure they are registered
        from app.database.models import User, Group, Location, Game, GamePlayer
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connection"""
    await engine.dispose()
