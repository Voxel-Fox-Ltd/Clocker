from datetime import datetime as dt

import discord
from discord.ext import vbu, commands

from cogs import utils


class UserCommands(vbu.Cog[vbu.Bot]):

    @staticmethod
    async def get_masks_for_user(
            db: vbu.Database,
            user: discord.Member) -> list[str]:
        """
        Get the masks that a user can use to clock in/out with.
        """

        # Get the masks from the database
        masks = await db.call(
            """
            SELECT
                mask
            FROM
                clock_masks
            WHERE
                guild_id = $1
            AND
                role_id = ANY($2::BIGINT[])
            """,
            user.guild.id,
            user.role_ids,
        )

        # Return the masks
        return [mask['mask'] for mask in masks]

    @commands.group(
        application_command_meta=commands.ApplicationCommandMeta(),
    )
    async def clock(self, _):
        """
        The parent group for the clock commands.
        """

        ...

    @clock.command(
        name="in",
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="mask",
                    description="The mask to use for the clock.",
                    type=discord.ApplicationCommandOptionType.string,
                    required=True,
                    autocomplete=True,
                ),
            ],
            guild_only=True,
        ),
    )
    async def clock_in(
            self,
            ctx: utils.types.GuildSlashContext,
            mask: str):
        """
        Clocks in to a specific mask.
        """

        return await self.clockother_in(ctx, ctx.interaction.user, mask)

    @clock.command(
        name="out",
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="mask",
                    description="The mask to use for the clock.",
                    type=discord.ApplicationCommandOptionType.string,
                    required=True,
                    autocomplete=True,
                ),
            ],
        ),
    )
    async def clock_out(
            self,
            ctx: utils.types.GuildSlashContext,
            mask: str):
        """
        Clocks out of one of your clocked in masks.
        """

        return await self.clockother_out(ctx, ctx.interaction.user, mask)

    @commands.group(
        application_command_meta=commands.ApplicationCommandMeta(
            permissions=discord.Permissions(manage_guild=True),
        ),
    )
    async def clockother(self, _):
        """
        The parent group for the clock commands.
        """

        ...

    @clockother.command(
        name="in",
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="user",
                    description="The user you want to manage.",
                    type=discord.ApplicationCommandOptionType.user,
                    required=True,
                ),
                discord.ApplicationCommandOption(
                    name="mask",
                    description="The mask to use for the clock.",
                    type=discord.ApplicationCommandOptionType.string,
                    required=True,
                    autocomplete=True,
                ),
            ],
            guild_only=True,
        ),
    )
    async def clockother_in(
            self,
            ctx: utils.types.GuildSlashContext,
            user: discord.Member,
            mask: str):
        """
        Clocks in to a specific mask.
        """

        # Defer because apparently this takes time :/
        await ctx.interaction.response.defer(ephemeral=True)

        # Open a db connection
        async with vbu.Database() as db:

            # Get the masks for the user
            allowed_masks = await self.get_masks_for_user(
                db,
                user,
            )

            # See if they're already clocked in for that mask
            clock_in = await utils.ClockIn.get_latest(
                db,
                ctx.guild.id,
                user.id,
                mask,
            )
            if clock_in:
                return await ctx.interaction.followup.send(
                    "You're already clocked in with that mask.",
                    ephemeral=True,
                )

            # See if they're allowed to use that mask
            if mask not in allowed_masks:
                return await ctx.interaction.followup.send(
                    "You don't have permission to use that mask.",
                    ephemeral=True,
                )

            # Create a new clock in
            clock_in = utils.ClockIn(
                id=None,
                guild_id=ctx.guild.id,
                user_id=user.id,
                mask=mask,
                clocked_in_at=dt.utcnow(),
                clocked_out_at=None,
            )
            await clock_in.update(db)

        # Send a message
        await ctx.interaction.followup.send(
            f"You've clocked in with the mask `{mask}`.",
            ephemeral=True,
        )

    @clockother.command(
        name="out",
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="user",
                    description="The user you want to manage.",
                    type=discord.ApplicationCommandOptionType.user,
                    required=True,
                ),
                discord.ApplicationCommandOption(
                    name="mask",
                    description="The mask to use for the clock.",
                    type=discord.ApplicationCommandOptionType.string,
                    required=True,
                    autocomplete=True,
                ),
            ],
        ),
    )
    async def clockother_out(
            self,
            ctx: utils.types.GuildSlashContext,
            user: discord.Member,
            mask: str):
        """
        Clocks out of one of your clocked in masks.
        """

        # Defer so we can have a nice loading message
        await ctx.interaction.response.defer(ephemeral=True)

        # Open a database connection
        async with vbu.Database() as db:

            # See if they're already clocked in with that mask
            clock_in = await utils.ClockIn.get_latest(
                db,
                ctx.guild.id,
                user.id,
                mask,
            )

            # If not, give them an error
            if not clock_in:
                return await ctx.interaction.followup.send(
                    "You're not clocked in with that mask.",
                    ephemeral=True,
                )

            # Otherwise, clock them out
            await clock_in.update(
                db,
                clocked_out_at=dt.utcnow(),
            )

        # Tell them we're done
        await ctx.interaction.followup.send(
            (
                f"You've clocked out of the mask **{mask}**. Your duration "
                f"for this session is "
                f"**{utils.format_timedelta(clock_in.duration)}**."
            ),
            ephemeral=True,
        )

    @clockother_in.autocomplete
    @clock_in.autocomplete
    async def clock_in_autocomplete(
            self,
            ctx: utils.types.GuildSlashContext,
            interaction: discord.AutocompleteInteraction):
        """
        Autocomplete for the clock in command.
        """

        # Get current clock ins for that user
        async with vbu.Database() as db:
            rows = await db.call(
                """
                SELECT
                    mask
                FROM
                    clock_masks
                WHERE
                    guild_id = $1
                """,
                ctx.interaction.guild_id,
            )

        # Return the masks that they're clocked in with
        options = [
            discord.ApplicationCommandOptionChoice(
                name=r['mask'],
                value=r['mask'],
            )
            for r in rows
        ]
        await interaction.response.send_autocomplete(options)

    @clockother_out.autocomplete
    @clock_out.autocomplete
    async def clock_out_autocomplete(
            self,
            ctx: utils.types.GuildSlashContext,
            interaction: discord.AutocompleteInteraction):
        """
        Autocomplete for the clock out command.
        """

        # Open a database connection
        async with vbu.Database() as db:

            # Get current clock ins for that user
            clock_ins = await utils.ClockIn.get_current(
                db,
                ctx.guild.id,
                ctx.author.id,
            )

        # Return the masks that they're clocked in with
        options = [
            discord.ApplicationCommandOptionChoice(
                name=clock_in.mask,
                value=clock_in.mask,
            )
            for clock_in in clock_ins
        ]
        await interaction.response.send_autocomplete(options)


def setup(bot: vbu.Bot):
    x = UserCommands(bot)
    bot.add_cog(x)
