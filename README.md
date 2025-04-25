# NoxBot 🎮🔔
**NoxBot** est un BOT Discord développé en **Python** avec **Discord.py**, conçu pour suivre les news d'un jeu Steam et les publier dans un canal Discord choisi.

## ⚙️ Prérequis
- **Python** (version : `3.12.0`)
- Un **terminal** compatible **Bash** (*sur WSL ou Unix-like*)
- Le fichier `.env` de configuration (*à récupérer sur le Drive*)

> 💡 **Optionnel**, utilisez un environnement virtuel pour isoler les dépendances :
```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 🚀 Setup
1. **Clonez le repo** :
```bash
git clone git@github.com:gaudesp/noxbot.git
cd noxbot
```

2. **Installez les dépendances** :
```bash
pip install -r requirements.txt
```

3. **Lancez le bot** :
```bash
python run_bot.py
```

4. **Inviter le bot** :
- INVIT accessible via : [https://discord.com/oauth2/authorize?client_id=1181244156757155971](https://discord.com/oauth2/authorize?client_id=1181244156757155971)

## 📦 Dépendances
- `aiosqlite` : Accès asynchrone à une base de données SQLite.
- `python-dotenv` : Chargement des variables d’environnement depuis un fichier .env.
- `sqlalchemy` : ORM pour la gestion de la base de données.
- `aiohttp` : Requêtes HTTP asynchrones, utilisé pour appeler l’API Steam.
- `discord.py` : Bibliothèque principale pour l’interaction avec l’API Discord.
- `Pillow` : Traitement d’images (notamment pour la vérification des images Steam).
- `requests` : Requêtes HTTP synchrones, utilisé dans certains traitements spécifiques.

## 🤝 Contribution
Lead developer : [@gaudesp](https://github.com/gaudesp)
