# daily_combo_bot

Bot Discord + Telegram qui publie chaque matin un combiné foot généré par l’IA (Mistral) à partir des matches du jour.

## Installation rapide
```bash
git clone …
cd daily_combo_bot
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # puis édite tes clés
python scheduler.py --run-once   # test en local
