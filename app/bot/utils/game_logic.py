import random
from typing import List, Tuple
from app.database.models import Location


def select_spies(player_ids: List[int], spy_percentage: int) -> List[int]:
    """Select spy players based on percentage"""
    total_players = len(player_ids)
    num_spies = max(1, int(total_players * spy_percentage / 100))
    
    return random.sample(player_ids, num_spies)


def shuffle_players(player_ids: List[int]) -> List[int]:
    """Shuffle player order for turns"""
    shuffled = player_ids.copy()
    random.shuffle(shuffled)
    return shuffled


def select_random_location(locations: List[Location]) -> Location:
    """Select random location from list"""
    return random.choice(locations)


def format_player_list(players: list, lang: str = "ru") -> str:
    """Format player list for display"""
    lines = []
    for i, player in enumerate(players, 1):
        name = player.user.first_name or player.user.username or f"User {player.user_id}"
        lines.append(f"{i}. {name}")
    
    return "\n".join(lines)


def get_location_name(location: Location, lang: str) -> str:
    """Get location name in specified language"""
    return location.name_translations.get(lang, location.name_translations.get("ru", "Unknown"))
