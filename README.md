# Clocker

Clocker aims to be a simple clock in/out bot for Discord.
It is currently in development.

## Usage

### Commands

#### User

- [x] clock in [mask]
    - [x] Check if the user has the mask they're trying to use.
    - [x] This will set the user as clocked in for the mask that they specified.
    - [x] If the user is already clocked in for that role, do nothing.
- [x] clock out [mask]
    - [x] !! Do NOT check if the user has the mask they're trying to use.
    - [x] This will set the user as clocked out for the mask that they specified.
    - [x] If the user is already clocked out of this guild, do nothing.

#### Management

- [x] information show [user]
    - [x] Show the user's clock in/out stats per day, including total time.
- [-] information showall [user]
    - [-] Show the user's clock in/out stats per day, including a log of when
    they clicked the button to remain clocked in.
- [x] information export
    - [x] Export information on the current guild to a CSV file. This should
    show each user (by their name and/or ID) and their total work time per day
    for a month period (past 30 days from the command run point).
- [ ] information clear
    - [ ] Clear all information on the current guild (mark it as deleted in
    the database).
    - [ ] If there are any users clocked in at the time, clock them out for
    their current activity, and log them in again for a new one of the same
    type so that no time is lost.

- [x] clockother in [user] [role]
    - [x] Clock the user in.
- [x] clockother out [user] [role]
    - [x] Clock the user out.
- [ ] clockother remove [user] [role] [duration]
    - [ ] Remove a duration of time from the given user.

- [x] settings masks list
    - [x] Show a list of masks that are currently set up
    (in form role -> list[mask] mapping).
- [x] settings masks add [role] [mask]
    - [x] Add a mask to the role.
- [x] settings masks remove [role] [mask]
    - [x] Remove a mask from the role.

### API

- [ ] GET /api/information?guild_id=XXXXXXXXXXXX
    - [ ] Get information on the current guild, returned as a CSV file.
    - [ ] Requires authentication in some regard. GDPR and all that.
