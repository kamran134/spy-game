from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.database.repositories.group import GroupRepository
from app.database.repositories.location import LocationRepository
from app.bot.middlewares.i18n import I18nMiddleware
from app.bot.filters.admin import IsAdminFilter


router = Router()


@router.message(Command("settings"), F.chat.type.in_(["group", "supergroup"]), IsAdminFilter())
async def cmd_settings(
    message: Message,
    group_repo: GroupRepository,
    i18n: I18nMiddleware,
    lang: str
):
    """Handle /settings command"""
    # Parse command arguments
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    # Ensure group exists
    group, _ = await group_repo.get_or_create(
        group_id=message.chat.id,
        title=message.chat.title
    )
    
    if not args:
        # Show current settings
        text = i18n.get_text(
            lang,
            "settings.current",
            language=group.language,
            min_players=group.min_players,
            max_players=group.max_players,
            spy_percentage=group.spy_percentage
        )
        await message.answer(text)
        return
    
    # Update settings
    if len(args) == 4:
        try:
            new_lang, min_players, max_players, spy_percentage = args
            
            if new_lang not in ["ru", "en", "az"]:
                raise ValueError("Invalid language")
            
            min_p = int(min_players)
            max_p = int(max_players)
            spy_p = int(spy_percentage)
            
            if not (2 <= min_p <= max_p <= 20):
                raise ValueError("Invalid player count")
            
            if not (0 < spy_p <= 50):
                raise ValueError("Invalid spy percentage")
            
            await group_repo.update_settings(
                group_id=message.chat.id,
                language=new_lang,
                min_players=min_p,
                max_players=max_p,
                spy_percentage=spy_p
            )
            
            text = i18n.get_text(
                new_lang,
                "settings.updated",
                language=new_lang,
                min_players=min_p,
                max_players=max_p,
                spy_percentage=spy_p
            )
            await message.answer(text)
            
        except (ValueError, IndexError):
            text = i18n.get_text(lang, "settings.error")
            await message.answer(text)
    else:
        text = i18n.get_text(lang, "settings.error")
        await message.answer(text)


@router.message(Command("addlocation"), F.chat.type.in_(["group", "supergroup"]), IsAdminFilter())
async def cmd_addlocation(
    message: Message,
    group_repo: GroupRepository,
    location_repo: LocationRepository,
    i18n: I18nMiddleware,
    lang: str
):
    """Handle /addlocation command"""
    # Ensure group exists
    await group_repo.get_or_create(
        group_id=message.chat.id,
        title=message.chat.title
    )
    
    # Parse location from command arguments
    args = message.text.replace("/addlocation", "").strip()
    
    if not args:
        text = i18n.get_text(lang, "location.add_prompt")
        await message.answer(text)
        return
    
    # Parse format: "Russian | English | Azerbaijan"
    parts = [p.strip() for p in args.split("|")]
    
    if len(parts) != 3:
        text = i18n.get_text(lang, "location.error")
        await message.answer(text)
        return
    
    ru_name, en_name, az_name = parts
    
    # Create location
    translations = {
        "ru": ru_name,
        "en": en_name,
        "az": az_name
    }
    
    await location_repo.create(
        name_translations=translations,
        group_id=message.chat.id
    )
    
    text = i18n.get_text(lang, "location.added", ru=ru_name, en=en_name, az=az_name)
    await message.answer(text)


@router.message(Command("settings"), F.chat.type.in_(["group", "supergroup"]), ~IsAdminFilter())
async def cmd_settings_not_admin(
    message: Message,
    i18n: I18nMiddleware,
    lang: str
):
    """Handle /settings from non-admin"""
    text = i18n.get_text(lang, "settings.not_admin")
    await message.answer(text)


@router.message(Command("addlocation"), F.chat.type.in_(["group", "supergroup"]), ~IsAdminFilter())
async def cmd_addlocation_not_admin(
    message: Message,
    i18n: I18nMiddleware,
    lang: str
):
    """Handle /addlocation from non-admin"""
    text = i18n.get_text(lang, "settings.not_admin")
    await message.answer(text)
