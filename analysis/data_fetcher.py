# analysis/data_fetcher.py
import datetime, asyncio, httpx, logging
from config import settings

log = logging.getLogger(__name__)

BASE    = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": settings.football_key}

# Ligues retenues (Big 5 + championnats d’été)
TOP_LEAGUES = {
    #39:  "Premier League",      # 🇬🇧
    #140: "La Liga",             # 🇪🇸
    #135: "Serie A",             # 🇮🇹
    #78:  "Bundesliga",          # 🇩🇪
    #61:  "Ligue 1",             # 🇫🇷
    71:  "Brasileirão A",       # 🇧🇷
    #253: "MLS",                 # 🇺🇸/🇨🇦
    98:  "J1 League",           # 🇯🇵
    94:  "K-League 1",          # 🇰🇷
    203: "Allsvenskan",         # 🇸🇪
    6: "FIFA Club World Cup",  # 🌍🏆
    #102: "Eliteserien",         # 🇳🇴
    #195: "Veikkausliiga",       # 🇫🇮
    #128: "Liga Profesional",    # 🇦🇷
}

def _keep(league_id: int) -> bool:
    """True si la ligue fait partie de la whitelist."""
    return league_id in TOP_LEAGUES


# ---------- Fixtures ----------
async def fetch_fixtures_today() -> list:
    day = datetime.datetime.now(settings.tz).date()
    url = f"{BASE}/fixtures?date={day}&timezone=Europe/Paris"
    log.info("📡 Appel fixtures : %s", url)

    try:
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.get(url, headers=HEADERS)
            r.raise_for_status()
            all_fx = r.json()["response"]
    except httpx.HTTPError as e:
        log.error("❌ Fixtures API error : %s", e)
        return []

    kept = [f for f in all_fx if _keep(f["league"]["id"])]
    log.info("⚽ Fixtures bruts : %s  |  gardés : %s", len(all_fx), len(kept))
    return kept


# ---------- Odds ----------
async def fetch_odds_today() -> list:
    day = datetime.datetime.now(settings.tz).date()
    url = (
        f"{BASE}/odds?date={day}&bookmaker=8"
        "&timezone=Europe/Paris"
    )
    log.info("📡 Appel odds : %s", url)

    try:
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.get(url, headers=HEADERS)
            r.raise_for_status()
            all_odds = r.json()["response"]
    except httpx.HTTPError as e:
        log.error("❌ Odds API error : %s", e)
        return []

    # --- filtrage sécurisé ---
    kept = []
    for o in all_odds:
        league_id = (
            o.get("fixture", {})
             .get("league", {})
             .get("id")
        )
        if league_id is None:
            continue               # structure incomplète → on ignore
        if _keep(league_id) and o.get("bookmakers"):
            kept.append(o)

    log.info("💰 Odds bruts : %s  |  gardés : %s", len(all_odds), len(kept))
    return kept


# ---------- Appel groupé ----------
async def fetch_today() -> tuple[list, list]:
    """Retourne (fixtures_filtrés, odds_filtrés)."""
    return await asyncio.gather(
        fetch_fixtures_today(),
        fetch_odds_today(),
    )
