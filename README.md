# N9 Tracker

A public Discord bot that gives any Discord server its own Valorant hub. Players link their Riot account through Riot Sign-On (RSO), then see their recent matches and a server leaderboard that compares everyone who opted in on that server.

Anyone can add N9 Tracker to their server. Each server's data is kept separate.

## Commands

| Command | What it does | Status |
|---|---|---|
| `/ping` | Check the bot is online | ✅ Live |
| `/valorant add` | Link your Riot account | ✅ Live (Riot ID verified via ACCOUNT-V1); moving to RSO login, see below |
| `/valorant profile` | Show your linked Riot account | ✅ Live |
| `/valorant remove` | Unlink your account and delete your data from that server | ✅ Live |
| `/valorant recent` | Your latest matches: map, agent, K/D/A, result | 🔒 Needs production access (VAL-MATCH-V1) |
| `/valorant leaderboard` | Server leaderboard of opted-in players | 🔒 Needs production access (VAL-MATCH-V1) |

## Account linking with Riot Sign-On (RSO)

Player data is only ever shown for players who log in with Riot themselves:

1. A user runs `/valorant add` in their server.
2. The bot replies with a private "Log in with Riot" link.
3. The user signs in on Riot's own login page and approves N9 Tracker.
4. Riot redirects back to N9 Tracker's callback, which confirms the account's PUUID and Riot ID.
5. The bot confirms in Discord: "✅ Linked Name#TAG."

N9 Tracker never sees Riot passwords. Until RSO credentials are issued, development builds verify a typed Riot ID through ACCOUNT-V1.

## Riot APIs used

| API | Used for |
|---|---|
| RSO (OAuth) | Proving the user owns the Riot account they link |
| ACCOUNT-V1 | Riot ID ↔ PUUID, and the account's active shard |
| VAL-MATCH-V1 | Match history (`matchlists/by-puuid`) and match details (`matches/{matchId}`) |
| VAL-CONTENT-V1 | Agent, map and game-mode names |
| VAL-STATUS-V1 | Server status and maintenance notices |

## Data and privacy

- Stored per linked player: Discord user ID, Discord server ID, Riot ID, PUUID, link date. Match stats are stored only for linked players.
- Data is shown only in the server where the player linked their account.
- `/valorant remove` deletes the player's data from that server immediately.
- There's no searching or tracking of players who haven't opted in, and no item store checker.
- Uses only the official Riot API: no scraping, no unofficial APIs.
- Free, with no ads and no paid features.

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

*N9 Tracker isn't endorsed by Riot Games and doesn't reflect the views or opinions of Riot Games or anyone officially involved in producing or managing Riot Games properties. Riot Games and all associated properties are trademarks or registered trademarks of Riot Games, Inc.*
