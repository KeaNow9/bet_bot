from telegram import Bot
from config import settings

CHAT_ID = "@mon_canal"  # ou -100123456789

async def send_to_telegram(text: str):
    if not settings.telegram_token:
        print("[telegram] token manquant")
        return
    await Bot(settings.telegram_token).send_message(
        chat_id=CHAT_ID, text=text, parse_mode="Markdown"
    )
