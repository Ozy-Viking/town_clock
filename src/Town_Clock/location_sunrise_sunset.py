import time
import datetime as dt
from pytz import timezone
from skyfield import almanac
from skyfield.api import wgs84, load
from timezonefinder import TimezoneFinder


def timezone_finder(latitude, longitude, altitude) -> dt.tzinfo:
    tf = TimezoneFinder()
    tz = tf.timezone_at(lng=longitude, lat=latitude)
    return timezone(tz)


def find_sunrise_sunset_times(latitude, longitude, altitude) -> dict:
    # Setting up Times
    zone = timezone_finder(latitude, longitude, altitude)
    now = zone.localize(dt.datetime.now())
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    midday = now.replace(hour=12, minute=0, second=0, microsecond=0)
    next_midday = midday + dt.timedelta(days=1)
    ts = load.timescale()
    t0 = ts.from_datetime(midnight)
    t1 = ts.from_datetime(next_midday)

    # Setting up Position and Function
    eph = load('de421.bsp')
    position = wgs84.latlon(latitude_degrees=latitude,
                            longitude_degrees=longitude,
                            elevation_m=altitude)
    f = almanac.dark_twilight_day(eph, position)
    times, events = almanac.find_discrete(t0, t1, f)

    # Running Function
    sunset_sunrise_times = {}
    previous_e = f(t0).item()
    idx = 0
    for t, e in zip(times, events):
        if e in [3, 4]:
            idx += 1
            sunset_sunrise_times[idx] = time.mktime(t.astimezone(zone).timetuple())

    return sunset_sunrise_times


if __name__ == '__main__':
    pass
