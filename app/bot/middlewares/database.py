from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import async_session_maker
from app.database.repositories.user import UserRepository
from app.database.repositories.group import GroupRepository
from app.database.repositories.location import LocationRepository
from app.database.repositories.game import GameRepository


class DatabaseMiddleware(BaseMiddleware):
    """Middleware to provide database session and repositories"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        async with async_session_maker() as session:
            data["session"] = session
            data["user_repo"] = UserRepository(session)
            data["group_repo"] = GroupRepository(session)
            data["location_repo"] = LocationRepository(session)
            data["game_repo"] = GameRepository(session)
            
            return await handler(event, data)
