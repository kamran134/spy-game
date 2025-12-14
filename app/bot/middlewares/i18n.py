import json
from pathlib import Path
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User


class I18nMiddleware(BaseMiddleware):
    """Middleware for internationalization"""
    
    def __init__(self):
        self.translations = {}
        self._load_translations()
    
    def _load_translations(self):
        """Load all translation files"""
        locales_dir = Path(__file__).parent.parent.parent / "locales"
        
        for locale_file in locales_dir.glob("*.json"):
            lang_code = locale_file.stem
            with open(locale_file, "r", encoding="utf-8") as f:
                self.translations[lang_code] = json.load(f)
    
    def get_text(self, lang: str, key: str, **kwargs) -> str:
        """Get translated text by key"""
        keys = key.split(".")
        text = self.translations.get(lang, self.translations["ru"])
        
        for k in keys:
            text = text.get(k, key)
            if isinstance(text, str):
                break
        
        if isinstance(text, str) and kwargs:
            return text.format(**kwargs)
        return text if isinstance(text, str) else key
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Get user language from event
        user: User = data.get("event_from_user")
        lang = "ru"  # default
        
        if user and user.language_code:
            # Map Telegram language codes to our codes
            if user.language_code.startswith("ru"):
                lang = "ru"
            elif user.language_code.startswith("en"):
                lang = "en"
            elif user.language_code.startswith("az"):
                lang = "az"
        
        # Check if user has preferred language in database
        user_repo = data.get("user_repo")
        if user_repo and user:
            db_user = await user_repo.get_by_id(user.id)
            if db_user:
                lang = db_user.language
        
        data["lang"] = lang
        data["i18n"] = self
        
        return await handler(event, data)
