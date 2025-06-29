import discord, asyncio
from config import settings

CHANNEL_ID = 123456789  # remplace par l’ID de ton salon

async def send_to_discord(text: str):
    if not settings.discord_token:
        print("[discord] token manquant")
        return
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        await client.get_channel(CHANNEL_ID).send(text)
        await client.close()

    await client.start(settings.discord_token)
