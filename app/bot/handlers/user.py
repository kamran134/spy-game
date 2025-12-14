from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER

from app.database.repositories.user import UserRepository
from app.database.repositories.group import GroupRepository
from app.bot.middlewares.i18n import I18nMiddleware
from app.bot.keyboards.inline import get_registration_keyboard


router = Router()


@router.message(CommandStart(), F.chat.type == "private")
async def cmd_start_private(
    message: Message,
    user_repo: UserRepository,
    i18n: I18nMiddleware,
    lang: str
):
    """Handle /start command in private chat"""
    user, created = await user_repo.get_or_create(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        language=lang
    )
    
    if created:
        text = i18n.get_text(lang, "start.welcome")
        await message.answer(text, reply_markup=get_registration_keyboard(i18n, lang))
    else:
        text = i18n.get_text(lang, "start.already_registered")
        await message.answer(text)


@router.callback_query(F.data == "register")
async def callback_register(
    callback: CallbackQuery,
    user_repo: UserRepository,
    i18n: I18nMiddleware,
    lang: str
):
    """Handle registration callback"""
    await user_repo.get_or_create(
        user_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name,
        language=lang
    )
    
    text = i18n.get_text(lang, "start.registered")
    await callback.answer(text, show_alert=True)


@router.message(Command("help"))
async def cmd_help(
    message: Message,
    i18n: I18nMiddleware,
    lang: str
):
    """Handle /help command"""
    text = i18n.get_text(lang, "help.text")
    await message.answer(text)


@router.my_chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def bot_added_to_group(
    event: ChatMemberUpdated,
    group_repo: GroupRepository
):
    """Handle bot being added to a group"""
    await group_repo.get_or_create(
        group_id=event.chat.id,
        title=event.chat.title,
        language="ru"
    )


@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def user_joined_group(
    event: ChatMemberUpdated,
    user_repo: UserRepository,
    group_repo: GroupRepository,
    i18n: I18nMiddleware
):
    """Handle user joining a group"""
    # Ensure group exists
    group, _ = await group_repo.get_or_create(
        group_id=event.chat.id,
        title=event.chat.title
    )
    
    # Check if user exists
    user = await user_repo.get_by_id(event.new_chat_member.user.id)
    
    if not user:
        # Send welcome message with registration button
        name = event.new_chat_member.user.first_name or event.new_chat_member.user.username
        text = i18n.get_text(group.language, "start.group_welcome", name=name)
        
        await event.bot.send_message(
            chat_id=event.chat.id,
            text=text,
            reply_markup=get_registration_keyboard(i18n, group.language)
        )
    else:
        # Auto-register: update user info
        await user_repo.get_or_create(
            user_id=event.new_chat_member.user.id,
            username=event.new_chat_member.user.username,
            first_name=event.new_chat_member.user.first_name,
            last_name=event.new_chat_member.user.last_name
        )
