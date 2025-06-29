import asyncio, schedule, time
from analysis.builder import build_combo
from poster import send_to_discord
from config import settings

async def job():
    msg = await build_combo()
    await send_to_discord(msg)

schedule.every().day.at(f"{settings.post_hour:02d}:00").do(
    lambda: asyncio.run(job())
)

print(f"[scheduler] Publiera chaque jour à {settings.post_hour:02d}:00 ({settings.tz})")
while True:
    schedule.run_pending()
    time.sleep(30)
