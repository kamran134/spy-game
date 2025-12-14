"""
Script to populate default locations in the database
Run this after first deployment to add default locations
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.database import async_session_maker
from app.database.repositories.location import LocationRepository


DEFAULT_LOCATIONS = [
    {"ru": "Больница", "en": "Hospital", "az": "Xəstəxana"},
    {"ru": "Школа", "en": "School", "az": "Məktəb"},
    {"ru": "Банк", "en": "Bank", "az": "Bank"},
    {"ru": "Ресторан", "en": "Restaurant", "az": "Restoran"},
    {"ru": "Аэропорт", "en": "Airport", "az": "Hava limanı"},
    {"ru": "Полиция", "en": "Police Station", "az": "Polis bölməsi"},
    {"ru": "Театр", "en": "Theater", "az": "Teatr"},
    {"ru": "Супермаркет", "en": "Supermarket", "az": "Supermarket"},
    {"ru": "Пляж", "en": "Beach", "az": "Çimərlik"},
    {"ru": "Кинотеатр", "en": "Cinema", "az": "Kinoteatr"},
    {"ru": "Университет", "en": "University", "az": "Universitet"},
    {"ru": "Отель", "en": "Hotel", "az": "Otel"},
    {"ru": "Казино", "en": "Casino", "az": "Kazino"},
    {"ru": "Церковь", "en": "Church", "az": "Kilsə"},
    {"ru": "Библиотека", "en": "Library", "az": "Kitabxana"},
    {"ru": "Парк", "en": "Park", "az": "Park"},
    {"ru": "Зоопарк", "en": "Zoo", "az": "Zoopark"},
    {"ru": "Музей", "en": "Museum", "az": "Muzey"},
    {"ru": "Стадион", "en": "Stadium", "az": "Stadion"},
    {"ru": "Метро", "en": "Subway", "az": "Metro"},
    {"ru": "Поезд", "en": "Train", "az": "Qatar"},
    {"ru": "Самолет", "en": "Airplane", "az": "Təyyarə"},
    {"ru": "Корабль", "en": "Ship", "az": "Gəmi"},
    {"ru": "Посольство", "en": "Embassy", "az": "Səfirlik"},
    {"ru": "Военная база", "en": "Military Base", "az": "Hərbi baza"},
    {"ru": "Космическая станция", "en": "Space Station", "az": "Kosmik stansiya"},
    {"ru": "Подводная лодка", "en": "Submarine", "az": "Sualtı qayıq"},
    {"ru": "Цирк", "en": "Circus", "az": "Sirk"},
    {"ru": "Завод", "en": "Factory", "az": "Zavod"},
    {"ru": "Ферма", "en": "Farm", "az": "Ferma"},
]


async def populate_locations():
    """Populate default locations"""
    async with async_session_maker() as session:
        repo = LocationRepository(session)
        
        # Check if locations already exist
        existing = await repo.get_default_locations()
        if existing:
            print(f"Default locations already exist ({len(existing)} locations)")
            return
        
        print("Adding default locations...")
        for loc_data in DEFAULT_LOCATIONS:
            await repo.create(name_translations=loc_data, group_id=None)
            print(f"Added: {loc_data['en']}")
        
        print(f"\n✅ Successfully added {len(DEFAULT_LOCATIONS)} default locations!")


if __name__ == "__main__":
    asyncio.run(populate_locations())
