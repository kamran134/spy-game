from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.bot.middlewares.i18n import I18nMiddleware


def get_registration_keyboard(i18n: I18nMiddleware, lang: str) -> InlineKeyboardMarkup:
    """Get registration keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=i18n.get_text(lang, "buttons.register"),
            callback_data="register"
        )]
    ])


def get_game_join_keyboard(i18n: I18nMiddleware, lang: str) -> InlineKeyboardMarkup:
    """Get game join keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=i18n.get_text(lang, "buttons.join"),
                callback_data="game_join"
            ),
            InlineKeyboardButton(
                text=i18n.get_text(lang, "buttons.pass"),
                callback_data="game_pass"
            )
        ]
    ])


def get_reveal_role_keyboard(i18n: I18nMiddleware, lang: str) -> InlineKeyboardMarkup:
    """Get reveal role keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=i18n.get_text(lang, "buttons.reveal_role"),
            callback_data="reveal_role"
        )]
    ])


def get_game_actions_keyboard(i18n: I18nMiddleware, lang: str) -> InlineKeyboardMarkup:
    """Get game actions keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=i18n.get_text(lang, "buttons.im_spy"),
                callback_data="spy_reveal"
            )
        ],
        [
            InlineKeyboardButton(
                text=i18n.get_text(lang, "buttons.accuse"),
                callback_data="accuse_player"
            )
        ]
    ])


def get_player_selection_keyboard(players: list, game_id: int) -> InlineKeyboardMarkup:
    """Get player selection keyboard for accusations"""
    buttons = []
    for player in players:
        name = player.user.first_name or player.user.username or f"User {player.user_id}"
        buttons.append([InlineKeyboardButton(
            text=name,
            callback_data=f"accuse_{game_id}_{player.user_id}"
        )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
