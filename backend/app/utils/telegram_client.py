import asyncio

from telegram import Bot
from telegram.error import TelegramError

from app.core.config import get_settings

settings = get_settings()


def _send_message_async(chat_id: str, message: str) -> None:
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    asyncio.run(bot.send_message(chat_id=chat_id, text=message))


def send_telegram_message(chat_id: str, message: str) -> None:
    if not settings.TELEGRAM_BOT_TOKEN or not chat_id:
        return

    try:
        _send_message_async(chat_id=chat_id, message=message)
    except (TelegramError, RuntimeError):
        return


def send_bulk_telegram_messages(chat_ids: list[str], message: str) -> None:
    for chat_id in chat_ids:
        send_telegram_message(chat_id, message)
