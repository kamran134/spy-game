from typing import Optional
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Game, GamePlayer, GameStatus


class GameRepository:
    """Repository for Game operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, game_id: int, load_players: bool = False) -> Optional[Game]:
        """Get game by ID"""
        query = select(Game).where(Game.id == game_id)
        if load_players:
            query = query.options(selectinload(Game.players).selectinload(GamePlayer.user))
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_active_game_for_group(self, group_id: int, load_players: bool = False) -> Optional[Game]:
        """Get active game for a group"""
        query = select(Game).where(
            and_(
                Game.group_id == group_id,
                Game.status.in_([GameStatus.REGISTRATION, GameStatus.IN_PROGRESS])
            )
        )
        if load_players:
            query = query.options(selectinload(Game.players).selectinload(GamePlayer.user))
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def create(self, group_id: int) -> Game:
        """Create new game"""
        game = Game(
            group_id=group_id,
            status=GameStatus.REGISTRATION
        )
        self.session.add(game)
        await self.session.commit()
        await self.session.refresh(game)
        return game
    
    async def add_player(self, game_id: int, user_id: int) -> Optional[GamePlayer]:
        """Add player to game"""
        # Check if player already in game
        result = await self.session.execute(
            select(GamePlayer).where(
                and_(
                    GamePlayer.game_id == game_id,
                    GamePlayer.user_id == user_id
                )
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing
        
        player = GamePlayer(
            game_id=game_id,
            user_id=user_id
        )
        self.session.add(player)
        await self.session.commit()
        await self.session.refresh(player)
        return player
    
    async def start_game(
        self,
        game_id: int,
        location_id: int,
        spy_user_ids: list[int],
        player_order: list[int]
    ) -> Optional[Game]:
        """Start the game"""
        game = await self.get_by_id(game_id, load_players=True)
        if not game:
            return None
        
        # Set game status
        game.status = GameStatus.IN_PROGRESS
        game.location_id = location_id
        game.started_at = datetime.utcnow()
        game.player_order = player_order
        game.current_player_index = 0
        
        # Mark spies
        for player in game.players:
            if player.user_id in spy_user_ids:
                player.is_spy = True
        
        await self.session.commit()
        await self.session.refresh(game)
        return game
    
    async def next_player(self, game_id: int) -> Optional[Game]:
        """Move to next player"""
        game = await self.get_by_id(game_id)
        if not game or game.status != GameStatus.IN_PROGRESS:
            return None
        
        game.current_player_index = (game.current_player_index + 1) % len(game.player_order)
        await self.session.commit()
        await self.session.refresh(game)
        return game
    
    async def eliminate_player(self, game_id: int, user_id: int) -> bool:
        """Eliminate player from game"""
        result = await self.session.execute(
            select(GamePlayer).where(
                and_(
                    GamePlayer.game_id == game_id,
                    GamePlayer.user_id == user_id
                )
            )
        )
        player = result.scalar_one_or_none()
        if player:
            player.is_eliminated = True
            await self.session.commit()
            return True
        return False
    
    async def end_game(self, game_id: int) -> Optional[Game]:
        """End the game"""
        game = await self.get_by_id(game_id)
        if not game:
            return None
        
        game.status = GameStatus.FINISHED
        game.finished_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(game)
        return game
