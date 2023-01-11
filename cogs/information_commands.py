from functools import reduce
import itertools
from typing import TYPE_CHECKING

import discord
from discord.ext import vbu, commands

from cogs import utils


class InformationCommands(vbu.Cog[vbu.Bot]):

    @commands.group(
        application_command_meta=commands.ApplicationCommandMeta(
            guild_only=True,
        ),
    )
    async def information(self, _):
        """
        Parent group for the information commands.
        """

        ...

    @information.command(
        name="show",
        application_command_meta=commands.ApplicationCommandMeta(
            guild_only=True,
            options=[
                discord.ApplicationCommandOption(
                    name="user",
                    description="The user to show information about.",
                    type=discord.ApplicationCommandOptionType.user,
                    required=True,
                ),
            ],
        ),
    )
    async def information_show(
            self,
            ctx: utils.types.GuildSlashContext,
            user: discord.Member):
        """
        Shows information about a user.
        """

        if ctx.interaction.guild_id is None:
            return
        await ctx.interaction.response.defer()
        async with vbu.Database() as db:
            all_clock_ins = await utils.ClockIn.get_all(
                db,
                ctx.interaction.guild_id,
                user.id,
            )

        # Get the valid clock ins
        all_clock_ins = [
            i
            for i in all_clock_ins
        ]

        # Format into an embed per mask
        embeds = []
        for mask, clock_ins in itertools.groupby(
                all_clock_ins,
                key=lambda i: i.mask.capitalize()):
            clock_ins = list(clock_ins)
            if not clock_ins:
                continue
            embed = vbu.Embed(title=mask)
            total_delta = reduce(
                lambda x, y: x + y,
                [i.duration for i in clock_ins],
            )
            embed.description = (
                f"This user has a total clock in time of "
                f"**{utils.format_timedelta(total_delta)}**."
            )
            field_line_list = []
            for ci in clock_ins:
                start = discord.utils.format_dt(ci.clocked_in_at, style="f")
                if ci.clocked_out_at is None:
                    field_line_list.append(
                        f"\N{BULLET} {start} - **Currently clocked in**"
                    )
                else:
                    end = discord.utils.format_dt(ci.clocked_out_at, style="f")
                    field_line_list.append(
                        f"\N{BULLET} {start} - {end} "
                        f"(**{utils.format_timedelta(ci.duration)}**)"
                    )
            embed.add_field(
                name="Clock Ins",
                value="\n".join(field_line_list),
                inline=False,
            )
            embeds.append(embed)

        # Send embeds
        if embeds:
            await ctx.interaction.followup.send(
                embeds=embeds,
            )
        else:
            await ctx.interaction.followup.send("No clock ins found.")

    # TODO information_show context command


def setup(bot: vbu.Bot):
    x = InformationCommands(bot)
    bot.add_cog(x)
