from typing import Optional
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Location


class LocationRepository:
    """Repository for Location operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, location_id: int) -> Optional[Location]:
        """Get location by ID"""
        result = await self.session.execute(
            select(Location).where(Location.id == location_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all_for_group(self, group_id: int) -> list[Location]:
        """Get all locations for a group (default + group-specific)"""
        result = await self.session.execute(
            select(Location).where(
                and_(
                    or_(
                        Location.group_id == group_id,
                        Location.group_id.is_(None)
                    ),
                    Location.is_active == True
                )
            )
        )
        return list(result.scalars().all())
    
    async def get_default_locations(self) -> list[Location]:
        """Get all default locations"""
        result = await self.session.execute(
            select(Location).where(
                and_(
                    Location.group_id.is_(None),
                    Location.is_active == True
                )
            )
        )
        return list(result.scalars().all())
    
    async def create(
        self,
        name_translations: dict,
        group_id: Optional[int] = None
    ) -> Location:
        """Create new location"""
        location = Location(
            name_translations=name_translations,
            group_id=group_id
        )
        self.session.add(location)
        await self.session.commit()
        await self.session.refresh(location)
        return location
    
    async def deactivate(self, location_id: int) -> bool:
        """Deactivate location"""
        location = await self.get_by_id(location_id)
        if location:
            location.is_active = False
            await self.session.commit()
            return True
        return False
