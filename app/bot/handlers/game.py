from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy import select

from app.database.repositories.user import UserRepository
from app.database.repositories.group import GroupRepository
from app.database.repositories.location import LocationRepository
from app.database.repositories.game import GameRepository
from app.database.models import GameStatus, Game
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


@router.message(Command("resumegame"), F.chat.type.in_(["group", "supergroup"]), IsAdminFilter())
async def cmd_resumegame(
    message: Message,
    group_repo: GroupRepository,
    game_repo: GameRepository,
    i18n: I18nMiddleware
):
    """Resume finished game (undo endgame)"""
    group = await group_repo.get_by_id(message.chat.id)

    # Get the last game (even if finished)
    result = await game_repo.session.execute(
        select(Game).where(Game.group_id == message.chat.id).order_by(Game.id.desc()).limit(1)
    )
    game = result.scalar_one_or_none()

    if not game or game.status != GameStatus.FINISHED:
        text = i18n.get_text(group.language, "game.game_not_finished")
        await message.answer(text)
        return

    await game_repo.resume_game(game.id)

    text = i18n.get_text(group.language, "game.game_resumed")
    await message.answer(text)


@router.message(Command("vote"), F.chat.type.in_(["group", "supergroup"]))
async def cmd_vote(
    message: Message,
    group_repo: GroupRepository,
    game_repo: GameRepository,
    location_repo: LocationRepository,
    i18n: I18nMiddleware
):
    """Vote for a player as spy"""
    group = await group_repo.get_by_id(message.chat.id)
    game = await game_repo.get_active_game_for_group(message.chat.id, load_players=True)

    if not game or game.status != GameStatus.IN_PROGRESS:
        text = i18n.get_text(group.language, "game.no_active_game")
        await message.answer(text)
        return

    # Check if voter is in game
    voter = next((p for p in game.players if p.user_id == message.from_user.id), None)
    if not voter:
        text = i18n.get_text(group.language, "game.not_in_game")
        await message.answer(text)
        return

    # Get voted user
    voted_for_id = None
    voted_name = None

    # Check if reply to message
    if message.reply_to_message and message.reply_to_message.from_user:
        voted_for_id = message.reply_to_message.from_user.id
        voted_name = message.reply_to_message.from_user.first_name or message.reply_to_message.from_user.username
    # Check for username in message
    elif message.text and len(message.text.split()) > 1:
        username = message.text.split()[1].lstrip('@')
        # Find player by username
        for p in game.players:
            if p.user.username and p.user.username.lower() == username.lower():
                voted_for_id = p.user_id
                voted_name = p.user.first_name or p.user.username
                break

    if not voted_for_id:
        text = i18n.get_text(group.language, "game.vote_usage")
        await message.answer(text)
        return

    # Check if voted user is in game
    voted_player = next((p for p in game.players if p.user_id == voted_for_id), None)
    if not voted_player:
        text = i18n.get_text(group.language, "game.vote_not_player")
        await message.answer(text)
        return

    # Check if voting for self
    if voted_for_id == message.from_user.id:
        text = i18n.get_text(group.language, "game.vote_self")
        await message.answer(text)
        return

    # Register vote
    await game_repo.add_vote(game.id, message.from_user.id, voted_for_id)

    text = i18n.get_text(group.language, "game.vote_registered", name=voted_name)
    await message.reply(text)

    # Check if all voted
    game = await game_repo.get_by_id(game.id, load_players=True)
    if len(game.votes) >= len(game.players):
        # Count votes
        from collections import Counter
        vote_counts = Counter(game.votes.values())
        most_voted_id, vote_count = vote_counts.most_common(1)[0]

        # Get names
        accused_player = next(p for p in game.players if p.user_id == most_voted_id)
        accused_name = accused_player.user.first_name or accused_player.user.username or f"User {most_voted_id}"

        # Show results
        results_text = "\n".join([
            f"• {next((p.user.first_name or p.user.username for p in game.players if p.user_id == uid), f'User {uid}')}: {count} голосов"
            for uid, count in vote_counts.most_common()
        ])

        text = i18n.get_text(group.language, "game.vote_results",
                            results=results_text,
                            accused=accused_name,
                            votes=vote_count)
        await message.answer(text)

        # Check if spy
        location = await location_repo.get_by_id(game.location_id)
        location_name = get_location_name(location, group.language)

        if accused_player.is_spy:
            spy_name = accused_player.user.first_name or accused_player.user.username
            text = i18n.get_text(group.language, "game.spy_found",
                                spy=spy_name,
                                location=location_name)
        else:
            spy_player = next(p for p in game.players if p.is_spy)
            spy_name = spy_player.user.first_name or spy_player.user.username
            text = i18n.get_text(group.language, "game.spy_escaped",
                                accused=accused_name,
                                spy=spy_name,
                                location=location_name)

        await message.answer(text)
        await game_repo.end_game(game.id)


@router.message(Command("guess"), F.chat.type.in_(["group", "supergroup"]))
async def cmd_guess(
    message: Message,
    group_repo: GroupRepository,
    game_repo: GameRepository,
    location_repo: LocationRepository,
    i18n: I18nMiddleware
):
    """Spy guesses the location with fuzzy matching"""
    from rapidfuzz import fuzz

    group = await group_repo.get_by_id(message.chat.id)
    game = await game_repo.get_active_game_for_group(message.chat.id, load_players=True)

    if not game or game.status != GameStatus.IN_PROGRESS:
        text = i18n.get_text(group.language, "game.no_active_game")
        await message.answer(text)
        return

    # Check if player is spy
    player = next((p for p in game.players if p.user_id == message.from_user.id), None)
    if not player:
        text = i18n.get_text(group.language, "game.not_in_game")
        await message.answer(text)
        return

    if not player.is_spy:
        text = i18n.get_text(group.language, "game.guess_not_spy")
        await message.answer(text)
        return

    # Get guess
    if not message.text or len(message.text.split()) < 2:
        text = i18n.get_text(group.language, "game.guess_usage")
        await message.answer(text)
        return

    guess = " ".join(message.text.split()[1:])

    # Get location
    location = await location_repo.get_by_id(game.location_id)
    location_name = get_location_name(location, group.language)
    spy_name = player.user.first_name or player.user.username

    # Fuzzy matching: calculate similarity
    similarity = fuzz.ratio(guess.lower(), location_name.lower())

    # Check result based on similarity
    if similarity >= 85:
        # High similarity (≥85%) - accept as correct
        text = i18n.get_text(group.language, "game.guess_correct",
                            location=location_name,
                            spy=spy_name)
        await message.answer(text)
        await game_repo.end_game(game.id)
    elif similarity >= 70:
        # Medium similarity (70-84%) - suggest correct name
        text = i18n.get_text(group.language, "game.guess_close",
                            location=location_name)
        await message.answer(text)
    else:
        # Low similarity (<70%) - wrong answer, game ends
        text = i18n.get_text(group.language, "game.guess_wrong",
                            location=location_name,
                            guess=guess)
        await message.answer(text)
        await game_repo.end_game(game.id)


# Auto-next handler for reply messages
@router.message(F.chat.type.in_(["group", "supergroup"]), F.reply_to_message)
async def handle_reply_to_turn(
    message: Message,
    bot: Bot,
    group_repo: GroupRepository,
    game_repo: GameRepository,
    i18n: I18nMiddleware
):
    """Auto /next when player replies to their turn message"""
    game = await game_repo.get_active_game_for_group(message.chat.id, load_players=True)

    if not game or game.status != GameStatus.IN_PROGRESS:
        return

    # Check if replying to bot's message about their turn
    if not message.reply_to_message.from_user.is_bot:
        return

    # Check if this is the current player
    current_user_id = game.player_order[game.current_player_index]
    if message.from_user.id != current_user_id:
        return

    # Check if bot's message mentions this user (your turn message)
    if not message.reply_to_message.text or "⏰" not in message.reply_to_message.text:
        return

    # Move to next player
    await game_repo.next_player(game.id)
    game = await game_repo.get_by_id(game.id, load_players=True)

    # Get next player
    next_user_id = game.player_order[game.current_player_index]
    next_player = next(p for p in game.players if p.user_id == next_user_id)

    # Mention player
    name = next_player.user.first_name or next_player.user.username or f"User {next_user_id}"
    text = i18n.get_text(group.language, "game.next_player", name=name)

    group = await group_repo.get_by_id(message.chat.id)

    try:
        await message.answer(text)
        await bot.send_message(
            message.chat.id,
            f"<a href='tg://user?id={next_user_id}'>{name}</a> " +
            i18n.get_text(group.language, "game.your_turn"),
            parse_mode="HTML"
        )
    except TelegramBadRequest:
        await message.answer(text)


# Non-admin game commands handlers
@router.message(Command("startgame"), F.chat.type.in_(["group", "supergroup"]), ~IsAdminFilter())
@router.message(Command("endregister"), F.chat.type.in_(["group", "supergroup"]), ~IsAdminFilter())
@router.message(Command("next"), F.chat.type.in_(["group", "supergroup"]), ~IsAdminFilter())
@router.message(Command("endgame"), F.chat.type.in_(["group", "supergroup"]), ~IsAdminFilter())
@router.message(Command("resumegame"), F.chat.type.in_(["group", "supergroup"]), ~IsAdminFilter())
async def cmd_game_not_admin(
    message: Message,
    i18n: I18nMiddleware,
    lang: str
):
    """Handle game commands from non-admin"""
    text = i18n.get_text(lang, "errors.not_admin")
    await message.answer(text)
