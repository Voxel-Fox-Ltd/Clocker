import discord
from discord.ext import vbu


__all__ = (
    'GuildSlashContext',
)


class _GuildInteraction(discord.CommandInteraction):
    user: discord.Member


class GuildSlashContext(vbu.SlashContext):
    guild: discord.Guild
    interaction: _GuildInteraction
