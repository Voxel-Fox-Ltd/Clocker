import collections

import discord
from discord.ext import vbu, commands
import asyncpg


class SettingsCommands(vbu.Cog[vbu.Bot]):

    @staticmethod
    def validate_mask_name(value: str) -> bool:
        """
        Checks if a mask name is valid.
        """

        return value.isidentifier()

    @commands.group(
        application_command_meta=commands.ApplicationCommandMeta(
            guild_only=True,
        ),
    )
    async def settings(self, _) -> None:
        """
        Parent group for the settings commands.
        """

        ...

    @settings.group(
        name="masks",
        application_command_meta=commands.ApplicationCommandMeta(
            guild_only=True,
        ),
    )
    async def settings_masks(self, _) -> None:
        """
        Parent group for the settings masks commands.
        """

        ...

    @settings_masks.command(
        name="add",
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="role",
                    description="The role that you want to add the mask to.",
                    type=discord.ApplicationCommandOptionType.role,
                    required=True,
                ),
                discord.ApplicationCommandOption(
                    name="mask",
                    description="The mask to add.",
                    type=discord.ApplicationCommandOptionType.string,
                    required=True,
                ),
            ],
            guild_only=True,
        ),
    )
    async def settings_masks_add(
            self,
            ctx: vbu.SlashContext,
            role: discord.Role,
            mask: str) -> None:
        """
        Add a mask to the server.
        """

        # Make sure the mask is valid
        if not self.validate_mask_name(mask):
            return await ctx.send(
                "That mask name is not a valid identifier.",
                ephemeral=True,
            )

        # Add the mask to the guild
        async with vbu.Database() as db:
            try:
                await db(
                    """
                    INSERT INTO
                        clock_masks
                        (
                            guild_id,
                            role_id,
                            mask
                        )
                    VALUES
                        (
                            $1,
                            $2,
                            $3
                        )
                    """,
                    ctx.interaction.guild_id, role.id, mask,
                )
            except asyncpg.exceptions.UniqueViolationError:
                await ctx.interaction.response.send_message(
                    "That mask already exists in your server.",
                    ephemeral=True,
                )
                return

        # And we done
        await ctx.interaction.response.send_message(
            f"Added the mask `{mask}` to {role.mention}.",
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @settings_masks.command(
        name="remove",
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="mask",
                    description="The mask to remove.",
                    type=discord.ApplicationCommandOptionType.string,
                    required=True,
                    autocomplete=True,
                ),
            ],
            guild_only=True,
        ),
    )
    async def settings_masks_remove(
            self,
            ctx: vbu.SlashContext,
            mask: str) -> None:
        """
        Remove a mask from your guild.
        """

        # Remove the mask
        async with vbu.Database() as db:
            rows = await db(
                """
                DELETE FROM
                    clock_masks
                WHERE
                    guild_id = $1
                AND
                    mask = $2
                RETURNING
                    role_id
                """,
                ctx.interaction.guild_id, mask,
            )

        # And we done
        if not rows:
            return await ctx.interaction.response.send_message(
                f"Couldn't find a mask with the name `{mask}`.",
                allowed_mentions=discord.AllowedMentions.none(),
            )
        return await ctx.interaction.response.send_message(
            f"Removed the mask `{mask}`.",
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @settings_masks.command(
        name="list",
        application_command_meta=commands.ApplicationCommandMeta(
            guild_only=True,
        ),
    )
    async def settings_masks_list(
            self,
            ctx: vbu.SlashContext) -> None:
        """
        List your guild's masks.
        """

        # Make sure we've got a guild
        if not ctx.interaction.guild_id:
            return  # Fail silently
        if not isinstance(ctx.interaction.guild, discord.Guild):
            raise AssertionError("Guild is None")

        # Get the masks
        async with vbu.Database() as db:
            rows = await db(
                """
                SELECT
                    *
                FROM
                    clock_masks
                WHERE
                    guild_id = $1
                """,
                ctx.interaction.guild_id,
            )

        # Sort it into a dict
        masks: dict[int, list[str]] = collections.defaultdict(list)
        for row in rows:
            masks[row["role_id"]].append(row["mask"])

        # Make the embed
        embed = vbu.Embed(use_random_colour=True)
        for role_id, mask_list in masks.items():
            role = ctx.interaction.guild.get_role(role_id)
            if role is None:
                continue
            embed.add_field(
                name=role.name,
                value="\n".join(f"\N{BULLET} `{m}`" for m in mask_list),
                inline=False,
            )

        # And we done
        await ctx.interaction.response.send_message(
            embeds=[embed],
            allowed_mentions=discord.AllowedMentions.none(),
        )


def setup(bot: vbu.Bot) -> None:
    x = SettingsCommands(bot)
    bot.add_cog(x)
