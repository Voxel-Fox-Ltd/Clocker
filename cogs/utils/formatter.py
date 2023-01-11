from datetime import timedelta

__all__ = (
    'format_timedelta',
)


def format_timedelta(td: timedelta) -> str:
    """
    Format a timedelta into a nice string of "X days, Y hours, Z minutes,
    and W seconds", skipping out items that don't exist.


    Parameters
    ----------
    td : timedelta
        The time that you want to format
    """

    # Get the days, hours, minutes, and seconds
    days, seconds = td.days, td.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    # Format the string
    string = ""
    if days:
        string += f"{abs(days)} day{'s' if days != 1 else ''}, "
    if hours:
        string += f"{abs(hours)} hour{'s' if hours != 1 else ''}, "
    if minutes:
        string += f"{abs(minutes)} minute{'s' if minutes != 1 else ''}, "
    if seconds:
        string += f"{abs(seconds)} second{'s' if seconds != 1 else ''}, "
    string = string[:-2]

    # Add negative time
    if td < timedelta(0):
        string = f"negative {string}"

    # Return the string
    return string

