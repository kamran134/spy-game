from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Group


class GroupRepository:
    """Repository for Group operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, group_id: int) -> Optional[Group]:
        """Get group by ID"""
        result = await self.session.execute(
            select(Group).where(Group.id == group_id)
        )
        return result.scalar_one_or_none()
    
    async def create(
        self,
        group_id: int,
        title: str,
        language: str = "ru"
    ) -> Group:
        """Create new group"""
        group = Group(
            id=group_id,
            title=title,
            language=language
        )
        self.session.add(group)
        await self.session.commit()
        await self.session.refresh(group)
        return group
    
    async def get_or_create(
        self,
        group_id: int,
        title: str,
        language: str = "ru"
    ) -> tuple[Group, bool]:
        """Get or create group, returns (group, created)"""
        group = await self.get_by_id(group_id)
        if group:
            # Update title if changed
            if group.title != title:
                group.title = title
                await self.session.commit()
            return group, False
        
        group = await self.create(group_id, title, language)
        return group, True
    
    async def update_settings(
        self,
        group_id: int,
        language: Optional[str] = None,
        min_players: Optional[int] = None,
        max_players: Optional[int] = None,
        spy_percentage: Optional[int] = None
    ) -> Optional[Group]:
        """Update group settings"""
        group = await self.get_by_id(group_id)
        if not group:
            return None
        
        if language:
            group.language = language
        if min_players is not None:
            group.min_players = min_players
        if max_players is not None:
            group.max_players = max_players
        if spy_percentage is not None:
            group.spy_percentage = spy_percentage
        
        await self.session.commit()
        await self.session.refresh(group)
        return group
