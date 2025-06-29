import asyncio
from telegram.ext import Application, CommandHandler
from analysis.builder import build_combo
from config import settings

async def combo_cmd(update, ctx):
    await update.message.reply_text(await build_combo(), parse_mode="Markdown")

async def main():
    app = Application.builder().token(settings.telegram_token).build()
    app.add_handler(CommandHandler("combo", combo_cmd))
    await app.start()
    await app.updater.start_polling()
    await asyncio.Future()  # bloque

if __name__ == "__main__":
    asyncio.run(main())
