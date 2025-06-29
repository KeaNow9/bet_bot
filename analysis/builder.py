# analysis/builder.py
import json, logging, asyncio
from .data_fetcher import fetch_today
from .llm_helper   import ask_mistral

log = logging.getLogger(__name__)

# ---------- Libellés FR ---------------------------------------------------------------
TRANSLATE = {
    "1":            "Victoire domicile",
    "X":            "Match nul",
    "2":            "Victoire extérieur",
    "over_1.5":     "Plus de 1,5 but",
    "under_1.5":    "Moins de 1,5 but",
    "over_2.5":     "Plus de 2,5 buts",
    "under_2.5":    "Moins de 2,5 buts",
}
def _fr_pick(code: str) -> str:
    return TRANSLATE.get(code, code)

# ---------- Fusion fixtures / odds ----------------------------------------------------
def _merge_fixtures_odds(fixtures: list, odds_list: list) -> list:
    odds_by_id = {o["fixture"]["id"]: o for o in odds_list if o.get("bookmakers")}
    merged = []
    for f in fixtures:
        fid = f["fixture"]["id"]
        merged.append({
            "id":          fid,
            "league":      f["league"]["name"],
            "home":        f["teams"]["home"]["name"],
            "away":        f["teams"]["away"]["name"],
            "utc_kickoff": f["fixture"]["date"],
            "odds":        odds_by_id.get(fid, {}),
        })
    return merged[:12]   # on n’envoie jamais plus de 12 matches au LLM

# ---------- Fallback maison (toujours un résultat) ------------------------------------
ALLOWED  = {"1","X","2","over_1.5","under_1.5","over_2.5","under_2.5"}
MIN_CONF = 60   # confiance minimale acceptée

def _fallback(matches: list) -> dict:
    """Construit un combiné simple si le LLM a échoué."""
    picks, used_ids = [], set()

    # 1️⃣ on prend deux victoires domicile “safe”
    for m in matches:
        if len(picks) >= 2:
            break
        picks.append({
            "id": m["id"],
            "pick": "1",
            "confidence": 65,
            "reason": "Forme supérieure à domicile."
        })
        used_ids.add(m["id"])

    total = 1.32 * 1.35      # cote fictive ≈1,78
    # 2️⃣ si < 1,70 → on ajoute un over_1.5
    if total < 1.70 and len(matches) > len(picks):
        extra = next(x for x in matches if x["id"] not in used_ids)
        picks.append({
            "id": extra["id"],
            "pick": "over_1.5",
            "confidence": 70,
            "reason": "Match potentiellement ouvert."
        })
        total *= 1.25        # ≈2,22

    return {
        "combo": picks,
        "total_odds": round(total, 2),
        "global_confidence": min(p["confidence"] for p in picks)
    }

# ---------- build_combo principal -----------------------------------------------------
async def build_combo() -> str:
    fixtures, odds = await fetch_today()
    matches_payload = _merge_fixtures_odds(fixtures, odds)
    log.info("✅ Matches retenus pour le LLM : %s", len(matches_payload))

    if not matches_payload:
        return "⚠️ Aucun match éligible aujourd’hui."

    # -- Appel LLM ---------------------------------------------------------------------
    combo = ask_mistral(json.dumps(matches_payload, ensure_ascii=False))

    # -- Filtrage pick/confiance -------------------------------------------------------
    valid, bad = [], []
    for p in combo.get("combo", []):
        if p.get("pick") in ALLOWED and p.get("confidence", 0) >= MIN_CONF:
            valid.append(p)
        else:
            bad.append(p)

    if bad:
        log.warning("Picks invalides ignorés : %s", bad)

    combo["combo"] = valid

    # -- Vérifications taille & cote ---------------------------------------------------
    need_fallback = (
        len(valid) < 2 or                       # moins de 2 paris valides
        combo.get("total_odds", 0) < 1.70       # cote trop basse ou manquante
    )

    if need_fallback:
        log.warning("Combiné invalide (taille ou cote) : %s", combo)
        combo = _fallback(matches_payload)
        log.info("↪️  Fallback généré : cote = %s", combo["total_odds"])

    # -- Mise en forme Discord ---------------------------------------------------------
    payload_by_id = {m["id"]: m for m in matches_payload}
    lines = ["👑 *Combiné IA du jour*"]
    for p in combo["combo"]:
        m = payload_by_id.get(p["id"], {"home": "?", "away": "?"})
        lines.append(
            f"• {m['home']} – {m['away']} → **{_fr_pick(p['pick'])}** "
            f"({p['confidence']} %)\n  _{p['reason']}_"
        )

    lines.append(f"\n*Cote totale* ≈ **{combo['total_odds']}**")
    return "\n".join(lines)
