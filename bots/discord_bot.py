# bots/discord_bot.py
import logging
logging.basicConfig(
    level=logging.INFO,                          # DEBUG pour plus de verbosité
    format="%(asctime)s │ %(levelname)s │ %(name)s │ %(message)s",
    datefmt="%H:%M:%S",
)


import os, asyncio, discord
from dotenv import load_dotenv
from analysis.builder import build_combo
from config import settings

intents = discord.Intents.default()
intents.message_content = True  # indispensable

bot = discord.Client(intents=intents)
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

@bot.event
async def on_ready():
    print(f"✅ Connecté sous {bot.user}")
    ch = bot.get_channel(CHANNEL_ID)
    if ch:
        await ch.send("Bot lancé ✔️")
    else:
        print("❌ CHANNEL_ID incorrect, channel introuvable")

@bot.event
async def on_message(msg):
    if msg.author.bot:
        return
    if msg.content.lower().startswith("!combo"):
        await msg.channel.send("⏳ Génération…")
        await msg.channel.send(await build_combo())

async def main():
    await bot.start(settings.discord_token)

if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
