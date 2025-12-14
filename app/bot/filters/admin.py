from aiogram.filters import Filter
from aiogram.types import Message
from aiogram import Bot


class IsAdminFilter(Filter):
    """Filter to check if user is admin in the chat"""
    
    async def __call__(self, message: Message, bot: Bot) -> bool:
        if message.chat.type == "private":
            return False
        
        member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        return member.status in ["creator", "administrator"]
