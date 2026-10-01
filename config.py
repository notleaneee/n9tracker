"""Loads settings from the .env file so secrets never live in the code."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")


def _optional_int(name: str) -> Optional[int]:
    value = os.getenv(name, "").strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        raise SystemExit(f"{name} in .env must be a number (got {value!r}).")


DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()

# Server to sync slash commands to instantly while developing. Leave empty to
# sync globally (global commands can take a while to appear in Discord).
DEV_GUILD_ID = _optional_int("DEV_GUILD_ID")

DATABASE_PATH = BASE_DIR / os.getenv("DATABASE_PATH", "valorant_bot.db").strip()

# Optional. Without it, /valorant add links accounts without checking they exist.
RIOT_API_KEY = os.getenv("RIOT_API_KEY", "").strip()

# Riot account routing region: americas, europe, or asia.
RIOT_REGION = os.getenv("RIOT_REGION", "americas").strip().lower()
