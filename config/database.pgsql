CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "citext";


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


CREATE TABLE IF NOT EXISTS clock_ins(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    mask TEXT NOT NULL,
    clock_in TIMESTAMP NOT NULL,
    clock_out TIMESTAMP
);
CREATE INDEX
    guild_id_user_id_mask_idx
IF NOT EXISTS
    ON clock_ins(guild_id, user_id, mask);


CREATE TABLE IF NOT EXISTS clock_masks(
    guild_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    mask CITEXT NOT NULL
);
CREATE INDEX
    guild_id_role_id_idx
IF NOT EXISTS
    ON clock_masks(guild_id, role_id);
