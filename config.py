from dotenv import load_dotenv
load_dotenv()                       # charge .env

import os
from dataclasses import dataclass
from zoneinfo import ZoneInfo

@dataclass(slots=True)
class Settings:
    discord_token: str = os.getenv("DISCORD_TOKEN", "")
    telegram_token: str = os.getenv("TELEGRAM_TOKEN", "")
    football_key:  str = os.getenv("FOOTBALL_API_KEY", "")
    mistral_key:   str = os.getenv("MISTRAL_API_KEY", "")
    llm_provider:  str = os.getenv("LLM_PROVIDER", "mistral")
    post_hour:     int = int(os.getenv("POST_HOUR", 8))
    tz:            ZoneInfo = ZoneInfo(os.getenv("TZ", "Europe/Paris"))

settings = Settings()