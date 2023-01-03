# Clocker

Clocker aims to be a simple clock in/out bot for Discord.
It is currently in development.

## Usage

### Commands

#### User

- [ ] clock in [mask]
    - [ ] Check if the user has the mask they're trying to use.
    - [ ] This will set the user as clocked in for the mask that they specified.
    - [ ] If the user is already clocked in for that role, do nothing.
- [ ] clock out [mask]
    - [ ] !! Do NOT check if the user has the mask they're trying to use.
    - [ ] This will set the user as clocked out for the mask that they specified.
    - [ ] If the user is already clocked out of this guild, do nothing.

#### Management

- [ ] information show [user]
    - [ ] Show the user's clock in/out stats per day, including total time.
- [ ] information showall [user]
    - [ ] Show the user's clock in/out stats per day, including a log of when
    they clicked the button to remain clocked in.
- [ ] information export
    - [ ] Export information on the current guild to a CSV file. This should
    show each user (by their name and/or ID) and their total work time per day
    for a month period (past 30 days from the command run point).
- [ ] information clear
    - [ ] Clear all information on the current guild (mark it as deleted in
    the database).
    - [ ] If there are any users clocked in at the time, clock them out for
    their current activity, and log them in again for a new one of the same
    type so that no time is lost.

- [ ] clockother in [user] [role]
    - [ ] Clock the user in.
- [ ] clockother out [user] [role]
    - [ ] Clock the user out.
- [ ] clockother remove [user] [role] [duration]
    - [ ] Remove a duration of time from the given user.

- [ ] settings masks list
    - [ ] Show a list of masks that are currently set up
    (in form role -> list[mask] mapping).
- [ ] settings masks add [role] [mask]
    - [ ] Add a mask to the role.
- [ ] settings masks remove [role] [mask]
    - [ ] Remove a mask from the role.

### API

- [ ] GET /api/information?guild_id=XXXXXXXXXXXX
    - [ ] Get information on the current guild, returned as a CSV file.
    - [ ] Requires authentication in some regard. GDPR and all that.
