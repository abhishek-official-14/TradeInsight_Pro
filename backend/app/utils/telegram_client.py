import requests

from app.core.config import get_settings

settings = get_settings()


def send_telegram_message(message: str) -> None:
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        return

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(
            url,
            json={
                'chat_id': settings.TELEGRAM_CHAT_ID,
                'text': message,
            },
            timeout=5,
        )
    except requests.RequestException:
        return
