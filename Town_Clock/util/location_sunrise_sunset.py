"""
Calculates sun position.
"""
import time
import datetime as dt
from typing import Any
from pytz import timezone
from skyfield import almanac
from skyfield.api import wgs84, load, Loader
from timezonefinder import TimezoneFinder


def timezone_finder(latitude: float, longitude: float, altitude: float) -> dt.tzinfo:
    tf = TimezoneFinder()
    tz = tf.timezone_at(lng=longitude, lat=latitude)
    return timezone(tz)


def find_sunrise_sunset_times(
        latitude: float, longitude: float, altitude: float
        ) -> dict[int, float]:
    # Setting up Times
    zone = timezone_finder(latitude, longitude, altitude)
    now = zone.localize(dt.datetime.now())  # type: ignore
    midnight: Any = now.replace(hour=0, minute=0, second=0, microsecond=0)  # type: ignore
    midday: Any = now.replace(hour=12, minute=0, second=0, microsecond=0)  # type: ignore
    next_midday: Any = midday + dt.timedelta(days=1)
    ts = load.timescale()  # type: ignore
    t0 = ts.from_datetime(midnight)  # type: ignore
    t1 = ts.from_datetime(next_midday)  # type: ignore

    # Setting up Position and Function
    eph: Loader = load("de421.bsp")  # type: ignore
    position = wgs84.latlon(  # type: ignore
        latitude_degrees=latitude, longitude_degrees=longitude, elevation_m=altitude
        )
    f = almanac.dark_twilight_day(eph, position)  # type: ignore
    times, events = almanac.find_discrete(t0, t1, f)  # type: ignore

    # Running Function
    sunset_sunrise_times = {}
    previous_e = f(t0).item()  # type: ignore
    idx: int = 0
    for t, e in zip(times, events):  # type: ignore
        if e in [3, 4]:
            idx += 1
            sunset_sunrise_times[idx] = time.mktime(t.astimezone(zone).timetuple())  # type: ignore

    return sunset_sunrise_times  # type: ignore
