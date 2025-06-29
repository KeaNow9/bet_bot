# analysis/llm_helper.py
import json, requests, logging
from config import settings

log = logging.getLogger(__name__)

# analysis/llm_helper.py
SYSTEM_PROMPT = """
Tu es un tipster professionnel francophone.

Objectif :
• Proposer un combiné le plus « safe » possible, mais avec une cote élevée.

Règles de sélection des paris :
1. Commence par choisir 2 paris (codes autorisés : 1, X, 2, over_1.5, under_1.5, over_2.5, under_2.5).
2. Calcule la cote totale :
   – Si elle est supérieure ou égale à 2,00 → garde ces 2 paris.
   – Sinon, ajoute un 3ᵉ pari.
3. Recaclule :
   – Si la nouvelle cote est ≥ 2,00 → garde le trio.
   – Si elle reste < 2,00, mais peut atteindre au moins 1,70 → accepte-la (c’est le minimum).
4. N’invente jamais d’ID : utilise STRICTEMENT ceux fournis.
5. Si « odds » est vide pour un match, estime la cote selon ta meilleure expertise.

Réponds STRICTEMENT au format JSON, en français :
{
  "combo":[
      {"id":<int>,
       "pick":"1/X/2/over_1.5/under_1.5/over_2.5/under_2.5",
       "confidence":0-100,
       "reason":"texte"}
  ],
  "total_odds":<float>,
  "global_confidence":<int>
}
"""





def ask_mistral(matches_json: str) -> dict:
    log.info("🧠 Prompt envoyé à Mistral (%s caractères)", len(matches_json))

    body = {
        "model": "mistral-tiny",
        "temperature": 0.3,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": matches_json}
        ],
        "response_format": {"type": "json_object"},
    }

    try:
        r = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.mistral_key}"},
            json=body,
            timeout=20,
        )
        r.raise_for_status()
        raw_json = r.json()
        log.debug("📬 Réponse brute : %s", raw_json)

        content = raw_json["choices"][0]["message"]["content"]
        return json.loads(content)          # → dict Python
    except (requests.RequestException, KeyError, json.JSONDecodeError) as e:
        log.error("❌ Erreur Mistral / parsing JSON : %s", e)
        # retourne un objet “vide” que builder.py saura gérer
        return {"combo": [], "total_odds": 0.0, "global_confidence": 0}
