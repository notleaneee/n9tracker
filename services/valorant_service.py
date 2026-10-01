"""Valorant/Riot logic that doesn't depend on Discord.

Parses Riot IDs and talks to the official Riot API, so the Discord commands
never call an external API directly.
"""

import asyncio
from dataclasses import dataclass
from typing import Optional
from urllib.parse import quote

import aiohttp

# Riot's limits: game name 3-16 characters, tagline 3-5 characters.
GAME_NAME_MIN, GAME_NAME_MAX = 3, 16
TAG_LINE_MIN, TAG_LINE_MAX = 3, 5


class InvalidRiotIdError(ValueError):
    """Raised when a Riot ID isn't in GameName#TagLine format."""


@dataclass(frozen=True)
class RiotId:
    game_name: str
    tag_line: str

    def __str__(self) -> str:
        return f"{self.game_name}#{self.tag_line}"


def parse_riot_id(raw: str) -> RiotId:
    """Split 'GameName#TagLine' into its parts, raising InvalidRiotIdError if malformed."""
    text = raw.strip()

    if "#" not in text:
        raise InvalidRiotIdError("Riot ID must include a `#`, like `TenZ#SEN`.")
    if text.count("#") > 1:
        raise InvalidRiotIdError("Riot ID can only contain one `#`, like `TenZ#SEN`.")

    game_name, tag_line = (part.strip() for part in text.split("#"))

    if not GAME_NAME_MIN <= len(game_name) <= GAME_NAME_MAX:
        raise InvalidRiotIdError(
            f"Game name must be {GAME_NAME_MIN}-{GAME_NAME_MAX} characters."
        )
    if not TAG_LINE_MIN <= len(tag_line) <= TAG_LINE_MAX:
        raise InvalidRiotIdError(
            f"Tagline must be {TAG_LINE_MIN}-{TAG_LINE_MAX} characters."
        )
    if not tag_line.isalnum():
        raise InvalidRiotIdError("Tagline can only contain letters and numbers.")

    return RiotId(game_name=game_name, tag_line=tag_line)


class RiotApiError(Exception):
    """The Riot API couldn't complete a request. The message is safe to show users."""


class RiotAccountNotFoundError(RiotApiError):
    """No Riot account exists with the given Riot ID."""


@dataclass(frozen=True)
class RiotAccount:
    puuid: str
    game_name: str
    tag_line: str


class RiotClient:
    """Minimal client for the official Riot API (https://developer.riotgames.com)."""

    def __init__(self, api_key: str, region: str):
        self.api_key = api_key
        self.base_url = f"https://{region}.api.riotgames.com"
        self._session: Optional[aiohttp.ClientSession] = None

    async def start(self) -> None:
        self._session = aiohttp.ClientSession(
            headers={"X-Riot-Token": self.api_key},
            timeout=aiohttp.ClientTimeout(total=10),
        )

    async def close(self) -> None:
        if self._session is not None:
            await self._session.close()

    async def get_account(self, riot_id: RiotId) -> RiotAccount:
        """Look up a Riot account, returning its official capitalization and PUUID."""
        path = (
            "/riot/account/v1/accounts/by-riot-id/"
            f"{quote(riot_id.game_name, safe='')}/{quote(riot_id.tag_line, safe='')}"
        )
        data = await self._get(path)
        return RiotAccount(puuid=data["puuid"], game_name=data["gameName"], tag_line=data["tagLine"])

    async def _get(self, path: str) -> dict:
        try:
            async with self._session.get(self.base_url + path) as resp:
                if resp.status == 200:
                    return await resp.json()
                if resp.status == 404:
                    raise RiotAccountNotFoundError("No Riot account found with that Riot ID.")
                if resp.status in (401, 403):
                    print(f"Riot API rejected the key (HTTP {resp.status}) - it may have expired.")
                    raise RiotApiError("The bot's Riot API key is invalid or expired. Ask the bot owner to update it.")
                if resp.status == 429:
                    raise RiotApiError("Riot's API is rate limiting the bot. Try again in a minute.")
                print(f"Riot API error: HTTP {resp.status} for {path}")
                raise RiotApiError("Riot's API returned an error. Try again later.")
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"Riot API connection error: {e!r}")
            raise RiotApiError("Couldn't reach Riot's API. Try again later.")
