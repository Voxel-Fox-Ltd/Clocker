from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from typing_extensions import Self
from datetime import datetime as dt, timedelta, date
import uuid

import discord

if TYPE_CHECKING:
    from discord.ext import vbu


__all__ = (
    'ClockIn',
)


class ClockIn:

    __slots__ = (
        '_id',
        'guild_id',
        'user_id',
        'mask',
        'clocked_in_at',
        'clocked_out_at',
    )

    def __init__(
            self,
            id: Optional[uuid.UUID],
            guild_id: int,
            user_id: int,
            mask: str,
            clocked_in_at: dt,
            clocked_out_at: Optional[dt] = None):
        self._id = id
        self.guild_id: int = guild_id
        self.user_id: int = user_id
        self.mask: str = mask
        self.clocked_in_at: dt = clocked_in_at
        self.clocked_out_at: Optional[dt] = clocked_out_at

    @property
    def clock_in_relative(self) -> str:
        return discord.utils.format_dt(self.clocked_in_at, style="f")

    @property
    def clock_out_relative(self) -> str:
        if self.clocked_out_at is None:
            raise ValueError()
        return discord.utils.format_dt(self.clocked_out_at, style="f")

    @property
    def id(self) -> str:
        if self._id is None:
            self._id = uuid.uuid4()
        return str(self._id)

    @id.setter
    def id(self, value: uuid.UUID | str | None):
        if isinstance(value, str):
            value = uuid.UUID(value)
        self._id = value

    @property
    def managed(self):
        return self.clocked_in_at.date() == date(2000, 1, 1)

    @property
    def duration(self) -> timedelta:
        if self.clocked_out_at:
            return self.clocked_out_at - self.clocked_in_at
        return dt.utcnow() - self.clocked_in_at

    @property
    def duration_with_negative(self) -> timedelta:
        if self.clocked_out_at:
            return self.clocked_out_at - self.clocked_in_at
        return dt.utcnow() - self.clocked_in_at

    @classmethod
    def from_row(cls, row: dict) -> Self:
        return cls(
            id=row['id'],
            guild_id=row['guild_id'],
            user_id=row['user_id'],
            mask=row['mask'],
            clocked_in_at=row['clock_in'],
            clocked_out_at=row['clock_out'],
        )

    @classmethod
    async def get_latest(
            cls,
            db: vbu.Database,
            guild_id: int,
            user_id: int,
            mask: str | None) -> Optional[Self]:
        """
        Get the latest clock in (that has not been clocked out) for a user with
        a given mask.
        """

        query = """
            SELECT
                *
            FROM
                clock_ins
            WHERE
                guild_id = $1
            AND
                user_id = $2
            AND
                mask = $3
            AND
                clock_out IS NULL
            ORDER BY
                clock_in DESC
            LIMIT 1
        """
        rows = await db.call(query, guild_id, user_id, mask)
        if not rows:
            return None
        return cls.from_row(rows[0])

    @classmethod
    async def get_current(
            cls,
            db: vbu.Database,
            guild_id: int,
            user_id: int) -> list[Self]:
        """
        Get the current clock ins for a user.
        """

        query = """
            SELECT
                *
            FROM
                clock_ins
            WHERE
                guild_id = $1
            AND
                user_id = $2
            AND
                clock_out IS NULL
            ORDER BY
                clock_in DESC
        """
        rows = await db.call(query, guild_id, user_id)
        return [cls.from_row(row) for row in rows]

    @classmethod
    async def get_all(
            cls,
            db: vbu.Database,
            guild_id: int,
            user_id: int) -> list[Self]:
        """
        Get all of the clock ins for a user.
        """

        query = """
            SELECT
                *
            FROM
                clock_ins
            WHERE
                guild_id = $1
            AND
                user_id = $2
            ORDER BY
                clock_in DESC
        """
        rows = await db.call(query, guild_id, user_id)
        return [cls.from_row(row) for row in rows]

    @classmethod
    async def get_all_for_guild(
            cls,
            db: vbu.Database,
            guild_id: int) -> list[Self]:
        """
        Get all of the clock ins for a guild.
        """

        query = """
            SELECT
                *
            FROM
                clock_ins
            WHERE
                guild_id = $1
            ORDER BY
                clock_in DESC
        """
        rows = await db.call(query, guild_id)
        return [cls.from_row(row) for row in rows]

    async def update(
            self,
            db: vbu.Database,
            **kwargs):
        """
        Update the clock in with the current values.
        """

        for i, o in kwargs.items():
            setattr(self, i, o)
        query = """
            INSERT INTO
                clock_ins
                (
                    id,
                    guild_id,
                    user_id,
                    mask,
                    clock_in,
                    clock_out
                )
            VALUES
                (
                    $1,
                    $2,
                    $3,
                    $4,
                    $5,
                    $6
                )
            ON CONFLICT
                (id)
            DO UPDATE SET
                guild_id = excluded.guild_id,
                user_id = excluded.user_id,
                mask = excluded.mask,
                clock_in = excluded.clock_in,
                clock_out = excluded.clock_out
        """
        await db.call(
            query,
            self.id,
            self.guild_id,
            self.user_id,
            self.mask,
            self.clocked_in_at,
            self.clocked_out_at,
        )
