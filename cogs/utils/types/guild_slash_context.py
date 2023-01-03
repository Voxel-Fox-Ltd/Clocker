from typing import TYPE_CHECKING

from discord.ext import vbu

if TYPE_CHECKING:
    import discord

__all__ = (
    'GuildSlashContext',
)


class _GuildInteraction(discord.CommandInteraction):
    user: discord.Member


class GuildSlashContext(vbu.SlashContext):
    guild: discord.Guild
    interaction: _GuildInteraction
