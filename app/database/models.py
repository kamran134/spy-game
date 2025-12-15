from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional
from sqlalchemy import String, BigInteger, Integer, Boolean, DateTime, JSON, ForeignKey, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class GameStatus(PyEnum):
    """Game status enum"""
    REGISTRATION = "registration"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    language: Mapped[str] = mapped_column(String(5), default="ru")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    game_players: Mapped[list["GamePlayer"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Group(Base):
    """Group/Chat model"""
    __tablename__ = "groups"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    language: Mapped[str] = mapped_column(String(5), default="ru")
    
    # Game settings
    min_players: Mapped[int] = mapped_column(Integer, default=4)
    max_players: Mapped[int] = mapped_column(Integer, default=10)
    spy_percentage: Mapped[int] = mapped_column(Integer, default=20)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    locations: Mapped[list["Location"]] = relationship(back_populates="group", cascade="all, delete-orphan")
    games: Mapped[list["Game"]] = relationship(back_populates="group", cascade="all, delete-orphan")


class Location(Base):
    """Location model"""
    __tablename__ = "locations"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Translations stored as JSON: {"ru": "Больница", "en": "Hospital", "az": "Xəstəxana"}
    name_translations: Mapped[dict] = mapped_column(JSON)
    
    # If group_id is NULL, it's a default location for all groups
    group_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("groups.id", ondelete="CASCADE"), nullable=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    group: Mapped[Optional["Group"]] = relationship(back_populates="locations")
    games: Mapped[list["Game"]] = relationship(back_populates="location")


class Game(Base):
    """Game session model"""
    __tablename__ = "games"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("groups.id", ondelete="CASCADE"))
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey("locations.id", ondelete="SET NULL"), nullable=True)
    
    status: Mapped[GameStatus] = mapped_column(Enum(GameStatus), default=GameStatus.REGISTRATION)
    
    # Game state
    current_player_index: Mapped[int] = mapped_column(Integer, default=0)
    player_order: Mapped[list] = mapped_column(JSON, default=list)  # List of user IDs in turn order
    votes: Mapped[dict] = mapped_column(JSON, default=dict)  # Dict of {voter_id: voted_for_id}
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    group: Mapped["Group"] = relationship(back_populates="games")
    location: Mapped[Optional["Location"]] = relationship(back_populates="games")
    players: Mapped[list["GamePlayer"]] = relationship(back_populates="game", cascade="all, delete-orphan")


class GamePlayer(Base):
    """Game player model (many-to-many with additional fields)"""
    __tablename__ = "game_players"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("games.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    
    is_spy: Mapped[bool] = mapped_column(Boolean, default=False)
    is_eliminated: Mapped[bool] = mapped_column(Boolean, default=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    game: Mapped["Game"] = relationship(back_populates="players")
    user: Mapped["User"] = relationship(back_populates="game_players")
