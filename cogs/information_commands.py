from functools import reduce
import itertools
from datetime import timedelta, date
from typing import Optional, cast
from asyncpg.connection import collections
import io
import csv

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
                ),
            ],
        ),
    )
    async def information_show(
            self,
            ctx: utils.types.GuildSlashContext,
            user: Optional[discord.Member] = None):
        """
        Shows information about a user.
        """

        user = user or ctx.author  # pyright: ignore
        user = cast(discord.Member, user)
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
                [i.duration_with_negative for i in clock_ins],
            )
            embed.description = (
                f"This user has a total clock in time of "
                f"**{utils.format_timedelta(total_delta)}**."
            )
            field_line_list = []
            for ci in clock_ins:
                if ci.clocked_out_at is None:
                    field_line_list.append(
                        f"\N{BULLET} {ci.clock_in_relative} - **Currently clocked in**"
                    )
                else:
                    if ci.managed and ci.duration.total_seconds() < 0:
                        field_line_list.append(
                            f"\N{BULLET} [Admin] Removed **{utils.format_timedelta(ci.duration)}**"
                        )
                    elif ci.managed:
                        field_line_list.append(
                            f"\N{BULLET} [Admin] Added **{utils.format_timedelta(ci.duration)}**"
                        )
                    else:
                        field_line_list.append(
                            f"\N{BULLET} {ci.clock_in_relative} - {ci.clock_out_relative} "
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

    @commands.context_command(
        name="Get clock ins for user."
    )
    async def clock_in_context_command(
            self,
            ctx: commands.SlashContext,
            user: discord.Member):
        await self.information_show(ctx, user)

    @information.command(
        name="export",
        application_command_meta=commands.ApplicationCommandMeta(
            guild_only=True,
        )
    )
    async def information_export(self, ctx: commands.SlashContext):
        """
        Export all of the users from the database into a CSV file.
        """

        # Defer so we can actually do stuff
        await ctx.interaction.response.defer()

        # Get all clockins
        assert ctx.interaction.guild_id
        async with vbu.Database() as db:
            all_clock_ins = await utils.ClockIn.get_all_for_guild(
                db,
                ctx.interaction.guild_id,
            )

        # Set up a dict to store each day's user clock in duration
        clock_in_durations: dict[date, dict[int, timedelta]]
        clock_in_durations = collections.defaultdict(dict)

        # Group the clockins by user ID
        for user_id, clockins in itertools.groupby(
                all_clock_ins,
                key=lambda i: i.user_id):

            # Group the clockins by day
            for day, clockins in itertools.groupby(
                    clockins,
                    key=lambda i: i.clocked_in_at.date()):

                # Get the total duration for the day
                total_duration = reduce(
                    lambda x, y: x + y,
                    [i.duration_with_negative for i in clockins],
                )

                # Add the duration to the dict
                clock_in_durations[day][user_id] = total_duration

        # Make a CSV file
        csv_file = io.StringIO()
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["Year", "Month", "Day", "User ID", "Duration"])
        for day, user_durations in clock_in_durations.items():
            for user_id, duration in user_durations.items():
                csv_writer.writerow([
                    day.year,
                    day.month,
                    day.day,
                    f"{user_id}\t",
                    duration.total_seconds(),
                ])

        # Send the file
        csv_file.seek(0)
        await ctx.interaction.followup.send(
            file=discord.File(
                csv_file,
                filename="clockins.csv",
            ),
        )

    @information.command(
        name="clear",
        application_command_meta=commands.ApplicationCommandMeta(
            guild_only=True,
        )
    )
    async def information_clear(self, ctx: commands.SlashContext):
        """
        Clear all of the clock ins from the database.
        """

        # Defer so we can actually do stuff
        await ctx.interaction.response.defer()

        # Delete all users
        assert ctx.interaction.guild_id
        async with vbu.Database() as db:
            await db.call(
                """
                DELETE FROM
                    clock_ins
                WHERE
                    guild_id = $1
                    AND clocked_out_at IS NOT NULL
                """,
                ctx.interaction.guild_id,
            )

        # Send a message
        await ctx.interaction.followup.send(
            "Cleared all clock ins from the database."
        )


def setup(bot: vbu.Bot):
    x = InformationCommands(bot)
    bot.add_cog(x)
