from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User


class UserRepository:
    """Repository for User operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create(
        self,
        user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        language: str = "ru"
    ) -> User:
        """Create new user"""
        user = User(
            id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language=language
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def get_or_create(
        self,
        user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        language: str = "ru"
    ) -> tuple[User, bool]:
        """Get or create user, returns (user, created)"""
        user = await self.get_by_id(user_id)
        if user:
            # Update user info if provided
            if username:
                user.username = username
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            await self.session.commit()
            return user, False
        
        user = await self.create(user_id, username, first_name, last_name, language)
        return user, True
    
    async def update_language(self, user_id: int, language: str) -> Optional[User]:
        """Update user language"""
        user = await self.get_by_id(user_id)
        if user:
            user.language = language
            await self.session.commit()
            await self.session.refresh(user)
        return user
