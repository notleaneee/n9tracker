"""The /valorant slash command group.

Implemented: add, profile, remove.
Planned: recent, leaderboard.
"""

from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from database.database import Database
from services.valorant_service import (
    InvalidRiotIdError,
    RiotApiError,
    RiotClient,
    parse_riot_id,
)


@app_commands.guild_only()
class Valorant(commands.GroupCog, group_name="valorant", group_description="Valorant account tracking"):
    def __init__(self, bot: commands.Bot, db: Database, riot: Optional[RiotClient]):
        self.bot = bot
        self.db = db
        self.riot = riot
        super().__init__()

    @app_commands.command(name="add", description="Link your Valorant account to this server")
    @app_commands.describe(riot_id="Your Riot ID, e.g. TenZ#SEN")
    async def add(self, interaction: discord.Interaction, riot_id: str):
        try:
            parsed = parse_riot_id(riot_id)
        except InvalidRiotIdError as e:
            await interaction.response.send_message(f"❌ {e}", ephemeral=True)
            return

        # The Riot API call can take a moment, so acknowledge the command first.
        await interaction.response.defer(ephemeral=True)

        game_name, tag_line, puuid = parsed.game_name, parsed.tag_line, None
        if self.riot is not None:
            try:
                account = await self.riot.get_account(parsed)
            except RiotApiError as e:
                await interaction.followup.send(f"❌ {e}", ephemeral=True)
                return
            # Use Riot's official capitalization (e.g. "tenz#sen" -> "TenZ#SEN").
            game_name, tag_line, puuid = account.game_name, account.tag_line, account.puuid

        replaced = self.db.link_account(
            discord_user_id=interaction.user.id,
            guild_id=interaction.guild_id,
            game_name=game_name,
            tag_line=tag_line,
            puuid=puuid,
        )

        verb = "Updated your linked account to" if replaced else "Linked"
        await interaction.followup.send(f"✅ {verb} **{game_name}#{tag_line}**.", ephemeral=True)

    @app_commands.command(name="profile", description="Show your linked Valorant account")
    async def profile(self, interaction: discord.Interaction):
        account = self.db.get_account(interaction.user.id, interaction.guild_id)
        if account is None:
            await interaction.response.send_message(
                "You haven't linked a Valorant account yet. Use /valorant add first.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(title="Valorant Account", color=discord.Color.red())
        embed.add_field(name="Riot ID", value=account.riot_id, inline=False)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="remove", description="Unlink your Valorant account and delete its data from this server")
    async def remove(self, interaction: discord.Interaction):
        removed = self.db.remove_account(interaction.user.id, interaction.guild_id)
        if removed:
            message = "✅ Your Valorant account has been unlinked and its data deleted from this server."
        else:
            message = "You don't have a Valorant account linked in this server."
        await interaction.response.send_message(message, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Valorant(bot, bot.db, bot.riot))
