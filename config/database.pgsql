CREATE TABLE IF NOT EXISTS guild_settings(
    guild_id BIGINT PRIMARY KEY,
    prefix TEXT
);
-- A default guild settings table.
-- This is required for VBU and should not be deleted.
-- You can add more columns to this table should you want to add more guild-specific
-- settings.


CREATE TABLE IF NOT EXISTS user_settings(
    user_id BIGINT PRIMARY KEY
);
-- A default guild settings table.
-- This is required for VBU and should not be deleted.
-- You can add more columns to this table should you want to add more user-specific
-- settings.
-- This table is not suitable for member-specific settings as there's no
-- guild ID specified.
