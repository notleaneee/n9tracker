"""SQLite storage for linked Valorant accounts."""

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

SCHEMA = """
CREATE TABLE IF NOT EXISTS linked_accounts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_user_id TEXT NOT NULL,
    guild_id        TEXT NOT NULL,
    game_name       TEXT NOT NULL,
    tag_line        TEXT NOT NULL,
    -- Riot's permanent player ID. Filled in once an authorized Riot API is connected.
    puuid           TEXT,
    added_at        TEXT NOT NULL,
    UNIQUE (discord_user_id, guild_id)
);
"""


@dataclass
class LinkedAccount:
    discord_user_id: int
    guild_id: int
    game_name: str
    tag_line: str
    puuid: Optional[str]
    added_at: str

    @property
    def riot_id(self) -> str:
        return f"{self.game_name}#{self.tag_line}"


class Database:
    def __init__(self, path: Path):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row

    def init(self) -> None:
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def link_account(
        self,
        discord_user_id: int,
        guild_id: int,
        game_name: str,
        tag_line: str,
        puuid: Optional[str] = None,
    ) -> bool:
        """Link a Riot ID, replacing any account already linked in this server.

        Returns True if an existing link was replaced.
        """
        replaced = self.get_account(discord_user_id, guild_id) is not None
        added_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.conn.execute(
            """
            INSERT INTO linked_accounts
                (discord_user_id, guild_id, game_name, tag_line, puuid, added_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT (discord_user_id, guild_id) DO UPDATE SET
                game_name = excluded.game_name,
                tag_line  = excluded.tag_line,
                puuid     = excluded.puuid,
                added_at  = excluded.added_at
            """,
            (str(discord_user_id), str(guild_id), game_name, tag_line, puuid, added_at),
        )
        self.conn.commit()
        return replaced

    def get_account(self, discord_user_id: int, guild_id: int) -> Optional[LinkedAccount]:
        row = self.conn.execute(
            "SELECT * FROM linked_accounts WHERE discord_user_id = ? AND guild_id = ?",
            (str(discord_user_id), str(guild_id)),
        ).fetchone()
        if row is None:
            return None
        return LinkedAccount(
            discord_user_id=int(row["discord_user_id"]),
            guild_id=int(row["guild_id"]),
            game_name=row["game_name"],
            tag_line=row["tag_line"],
            puuid=row["puuid"],
            added_at=row["added_at"],
        )
