"""Valorant Friends Tracker - entry point.

Run with:  python bot.py
"""

import discord
from discord.ext import commands

import config
from database.database import Database
from services.valorant_service import RiotClient

EXTENSIONS = ["commands.valorant"]


class ValorantBot(commands.Bot):
    def __init__(self):
        # Slash commands don't need message content, so default intents are enough.
        super().__init__(command_prefix=commands.when_mentioned, intents=discord.Intents.default())
        self.db = Database(config.DATABASE_PATH)
        self.riot = RiotClient(config.RIOT_API_KEY, config.RIOT_REGION) if config.RIOT_API_KEY else None

    async def setup_hook(self):
        self.db.init()
        if self.riot is not None:
            await self.riot.start()
        else:
            print("RIOT_API_KEY not set - /valorant add will link accounts without verifying them")

        for extension in EXTENSIONS:
            await self.load_extension(extension)

        if config.DEV_GUILD_ID:
            guild = discord.Object(id=config.DEV_GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            print(f"Synced {len(synced)} command(s) to dev server {config.DEV_GUILD_ID}")
        else:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} global command(s) (may take a while to appear)")

    async def on_ready(self):
        print(f"✅ Valorant Tracker connected as {self.user} (ID: {self.user.id})")
        print(f"   Serving {len(self.guilds)} server(s)")

    async def close(self):
        await super().close()
        if self.riot is not None:
            await self.riot.close()
        self.db.close()


bot = ValorantBot()


@bot.tree.command(name="ping", description="Check whether the bot is online")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Valorant Tracker is online! 🟢")


if __name__ == "__main__":
    if not config.DISCORD_TOKEN:
        raise SystemExit("DISCORD_TOKEN is missing. Add it to valorant-bot/.env first.")
    bot.run(config.DISCORD_TOKEN)
