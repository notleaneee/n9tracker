# Valorant Friends Tracker

A private, non-commercial Discord bot for a single friend group's server. Members link their own Riot account, and the bot will show their recent Valorant matches and a private leaderboard that compares friends within that server.

## Status

| Feature | Status | Riot API |
|---|---|---|
| `/ping` | ✅ Working | — |
| `/valorant add riot_id:Name#Tag` — link your Riot account | ✅ Working | ACCOUNT-V1 (verifies the Riot ID exists, stores the PUUID) |
| `/valorant profile` — show your linked account | ✅ Working | — |
| `/valorant recent` — your latest matches | ⏳ Waiting for production key | VAL-MATCH-V1 |
| `/valorant leaderboard` — friends-only leaderboard for the server | ⏳ Waiting for production key | VAL-MATCH-V1 |
| `/valorant remove` — unlink your account | Planned | — |

## How it uses Riot data

- Only players who link their **own** account with `/valorant add` are tracked. There is no searching or tracking of other players.
- Data is shown only inside the Discord server where the player linked their account.
- Stored per player: Discord user ID, server ID, Riot ID, PUUID and the date linked. Match stats will be stored only for linked players.
- Uses only the official Riot API (no scraping and no third-party stat sites), and respects Riot's rate limits.
- Non-commercial: no ads, payments or paid features.

## Tech

Python 3.9+, [discord.py](https://discordpy.readthedocs.io/) slash commands, SQLite, and the official [Riot API](https://developer.riotgames.com).

```
bot.py                       # entry point: connects to Discord, registers commands
config.py                    # loads settings from .env
commands/valorant.py         # /valorant command group
services/valorant_service.py # Riot ID parsing + Riot API client
database/database.py         # SQLite storage for linked accounts
```

## Running it yourself

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in DISCORD_TOKEN and RIOT_API_KEY
python bot.py
```

Secrets live only in `.env`, which is excluded from git.

---

*Valorant Friends Tracker isn't endorsed by Riot Games and doesn't reflect the views or opinions of Riot Games or anyone officially involved in producing or managing Riot Games properties. Riot Games and all associated properties are trademarks or registered trademarks of Riot Games, Inc.*
