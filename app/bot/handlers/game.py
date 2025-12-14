from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from app.database.repositories.user import UserRepository
from app.database.repositories.group import GroupRepository
from app.database.repositories.location import LocationRepository
from app.database.repositories.game import GameRepository
from app.database.models import GameStatus
from app.bot.middlewares.i18n import I18nMiddleware
from app.bot.filters.admin import IsAdminFilter
from app.bot.keyboards.inline import (
    get_game_join_keyboard,
    get_reveal_role_keyboard,
    get_game_actions_keyboard,
    get_player_selection_keyboard
)
from app.bot.utils.game_logic import (
    select_spies,
    shuffle_players,
    select_random_location,
    format_player_list,
    get_location_name
)


router = Router()


@router.message(Command("startgame"), F.chat.type.in_(["group", "supergroup"]), IsAdminFilter())
async def cmd_startgame(
    message: Message,
    group_repo: GroupRepository,
    game_repo: GameRepository,
    i18n: I18nMiddleware,
    lang: str
):
    """Start game registration"""
    # Ensure group exists
    group, _ = await group_repo.get_or_create(
        group_id=message.chat.id,
        title=message.chat.title
    )
    
    # Check if game already active
    active_game = await game_repo.get_active_game_for_group(message.chat.id)
    if active_game:
        text = i18n.get_text(group.language, "game.already_started")
        await message.answer(text)
        return
    
    # Create new game
    await game_repo.create(group_id=message.chat.id)
    
    # Send announcement
    text = i18n.get_text(group.language, "game.announcement")
    await message.answer(text, reply_markup=get_game_join_keyboard(i18n, group.language))


@router.callback_query(F.data == "game_join")
async def callback_game_join(
    callback: CallbackQuery,
    user_repo: UserRepository,
    group_repo: GroupRepository,
    game_repo: GameRepository,
    i18n: I18nMiddleware
):
    """Handle player joining game"""
    # Check if user is registered
    user = await user_repo.get_by_id(callback.from_user.id)
    if not user:
        text = i18n.get_text("ru", "game.not_registered")
        await callback.answer(text, show_alert=True)
        return
    
    # Get active game
    group = await group_repo.get_by_id(callback.message.chat.id)
    game = await game_repo.get_active_game_for_group(callback.message.chat.id, load_players=True)
    
    if not game or game.status != GameStatus.REGISTRATION:
        text = i18n.get_text(group.language, "game.no_active_game")
        await callback.answer(text, show_alert=True)
        return
    
    # Check if already joined
    if any(p.user_id == callback.from_user.id for p in game.players):
        text = i18n.get_text(group.language, "game.already_joined")
        await callback.answer(text, show_alert=True)
        return
    
    # Check max players
    if len(game.players) >= group.max_players:
        text = i18n.get_text(group.language, "game.too_many_players", max_players=group.max_players)
        await callback.answer(text, show_alert=True)
        return
    
    # Add player
    await game_repo.add_player(game.id, callback.from_user.id)
    
    text = i18n.get_text(group.language, "game.joined")
    await callback.answer(text)
    
    # Update game message
    game = await game_repo.get_by_id(game.id, load_players=True)
    players_text = format_player_list(game.players, group.language)
    status_text = i18n.get_text(
        group.language,
        "game.players_list",
        count=len(game.players),
        players=players_text
    )
    
    try:
        await callback.message.edit_text(
            callback.message.text + "\n\n" + status_text,
            reply_markup=callback.message.reply_markup
        )
    except TelegramBadRequest:
        pass


@router.callback_query(F.data == "game_pass")
async def callback_game_pass(
    callback: CallbackQuery,
    i18n: I18nMiddleware,
    lang: str
):
    """Handle player passing game"""
    text = i18n.get_text(lang, "game.passed")
    await callback.answer(text)


@router.message(Command("endregister"), F.chat.type.in_(["group", "supergroup"]), IsAdminFilter())
async def cmd_endregister(
    message: Message,
    bot: Bot,
    group_repo: GroupRepository,
    location_repo: LocationRepository,
    game_repo: GameRepository,
    i18n: I18nMiddleware
):
    """End registration and start game"""
    group = await group_repo.get_by_id(message.chat.id)
    game = await game_repo.get_active_game_for_group(message.chat.id, load_players=True)
    
    if not game or game.status != GameStatus.REGISTRATION:
        text = i18n.get_text(group.language, "game.no_active_game")
        await message.answer(text)
        return
    
    # Check player count
    if len(game.players) < group.min_players:
        text = i18n.get_text(group.language, "game.not_enough_players", min_players=group.min_players)
        await message.answer(text)
        return
    
    if len(game.players) > group.max_players:
        text = i18n.get_text(group.language, "game.too_many_players", max_players=group.max_players)
        await message.answer(text)
        return
    
    # Get locations
    locations = await location_repo.get_all_for_group(message.chat.id)
    if not locations:
        await message.answer("❌ No locations available!")
        return
    
    # Select random location
    location = select_random_location(locations)
    
    # Select spies
    player_ids = [p.user_id for p in game.players]
    spy_ids = select_spies(player_ids, group.spy_percentage)
    
    # Shuffle player order
    player_order = shuffle_players(player_ids)
    
    # Start game
    await game_repo.start_game(game.id, location.id, spy_ids, player_order)
    
    # Send game started message
    text = i18n.get_text(group.language, "game.started")
    await message.answer(text, reply_markup=get_reveal_role_keyboard(i18n, group.language))
    
    # Send roles to private messages (if user started bot)
    location_name = get_location_name(location, group.language)
    
    for player in game.players:
        is_spy = player.user_id in spy_ids
        
        try:
            if is_spy:
                pm_text = i18n.get_text(group.language, "game.location_spy")
            else:
                pm_text = i18n.get_text(group.language, "game.location_normal", location=location_name)
            
            await bot.send_message(player.user_id, pm_text)
        except TelegramBadRequest:
            # User hasn't started bot yet
            pass


@router.callback_query(F.data == "reveal_role")
async def callback_reveal_role(
    callback: CallbackQuery,
    group_repo: GroupRepository,
    location_repo: LocationRepository,
    game_repo: GameRepository,
    i18n: I18nMiddleware
):
    """Reveal role to player"""
    # This callback can come from group, need to handle carefully
    if callback.message.chat.type == "private":
        await callback.answer("Use this button in the group!", show_alert=True)
        return
    
    group = await group_repo.get_by_id(callback.message.chat.id)
    game = await game_repo.get_active_game_for_group(callback.message.chat.id, load_players=True)
    
    if not game or game.status != GameStatus.IN_PROGRESS:
        text = i18n.get_text(group.language, "game.no_active_game")
        await callback.answer(text, show_alert=True)
        return
    
    # Find player
    player = next((p for p in game.players if p.user_id == callback.from_user.id), None)
    if not player:
        await callback.answer("You are not in this game!", show_alert=True)
        return
    
    # Get location
    location = await location_repo.get_by_id(game.location_id)
    location_name = get_location_name(location, group.language)
    
    # Show role
    if player.is_spy:
        text = i18n.get_text(group.language, "game.location_spy")
    else:
        text = i18n.get_text(group.language, "game.location_normal", location=location_name)
    
    await callback.answer(text, show_alert=True)


@router.message(Command("next"), F.chat.type.in_(["group", "supergroup"]), IsAdminFilter())
async def cmd_next(
    message: Message,
    bot: Bot,
    group_repo: GroupRepository,
    game_repo: GameRepository,
    i18n: I18nMiddleware
):
    """Move to next player"""
    group = await group_repo.get_by_id(message.chat.id)
    game = await game_repo.get_active_game_for_group(message.chat.id, load_players=True)
    
    if not game or game.status != GameStatus.IN_PROGRESS:
        text = i18n.get_text(group.language, "game.no_active_game")
        await message.answer(text)
        return
    
    # Move to next player
    await game_repo.next_player(game.id)
    game = await game_repo.get_by_id(game.id, load_players=True)
    
    # Get current player
    current_user_id = game.player_order[game.current_player_index]
    current_player = next(p for p in game.players if p.user_id == current_user_id)
    
    # Mention player
    name = current_player.user.first_name or current_player.user.username or f"User {current_user_id}"
    text = i18n.get_text(group.language, "game.next_player", name=name)
    
    try:
        await message.answer(text)
        # Try to mention user
        await bot.send_message(
            message.chat.id,
            f"<a href='tg://user?id={current_user_id}'>{name}</a> " + 
            i18n.get_text(group.language, "game.your_turn"),
            parse_mode="HTML"
        )
    except TelegramBadRequest:
        await message.answer(text)


@router.message(Command("endgame"), F.chat.type.in_(["group", "supergroup"]), IsAdminFilter())
async def cmd_endgame(
    message: Message,
    group_repo: GroupRepository,
    game_repo: GameRepository,
    i18n: I18nMiddleware
):
    """End current game"""
    group = await group_repo.get_by_id(message.chat.id)
    game = await game_repo.get_active_game_for_group(message.chat.id)
    
    if not game:
        text = i18n.get_text(group.language, "game.no_active_game")
        await message.answer(text)
        return
    
    await game_repo.end_game(game.id)
    
    text = i18n.get_text(group.language, "game.game_ended")
    await message.answer(text)


# Non-admin game commands handlers
@router.message(Command("startgame"), F.chat.type.in_(["group", "supergroup"]), ~IsAdminFilter())
@router.message(Command("endregister"), F.chat.type.in_(["group", "supergroup"]), ~IsAdminFilter())
@router.message(Command("next"), F.chat.type.in_(["group", "supergroup"]), ~IsAdminFilter())
@router.message(Command("endgame"), F.chat.type.in_(["group", "supergroup"]), ~IsAdminFilter())
async def cmd_game_not_admin(
    message: Message,
    i18n: I18nMiddleware,
    lang: str
):
    """Handle game commands from non-admin"""
    text = i18n.get_text(lang, "errors.not_admin")
    await message.answer(text)
