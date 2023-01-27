"""
data.py

"""
import time
import datetime


def mod_freq(tm: float | int, freq: float = 0) -> float | int:
    """
    Mod Time to show clean minutes

    Args:
        tm (float): Input time in seconds.
        freq (float, optional): Frequency of pulses. Defaults to 0.

    Raises:
        ValueError: When a given variable is not a number.
        ValueError: When freq is less than 0.

    Returns:
        float: Seconds rounded to the nearest minute. Unless freq is set.
    """
    if type(tm) not in (float, int):
        raise ValueError("Not a Number.")

    if freq > 0:
        freq = freq
    elif freq == 0:
        freq = 60
    else:
        raise ValueError("Number less than 0.")
    tm_mod = tm % freq

    match tm:  # type: ignore
        case tm if tm_mod >= freq / 2:
            return tm + (freq - tm_mod)
        case tm if tm_mod < freq / 2:
            return tm - tm_mod


def to_from_iso_format(time_stamp: float) -> datetime.datetime:
    """

    Todo:
        Work out what this function is for.

    Args:
        time_stamp: float: seconds since epoch.

    Returns:
        datetime.datetime
    """
    it = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time_stamp))
    return datetime.datetime.fromisoformat(it)
