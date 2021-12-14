import time
import datetime as dt
from pytz import timezone
from skyfield import almanac
from skyfield.api import wgs84, load
from timezonefinder import TimezoneFinder


def timezone_finder(latitude,longitude, altitude) -> dt.tzinfo:
    tf = TimezoneFinder()
    tz = tf.timezone_at(lng=longitude, lat=latitude)
    return timezone(tz)


def find_sunrise_sunset_times(latitude, longitude, altitude) -> dict:
    # Setting up Times
    zone = timezone_finder(latitude, longitude, altitude)
    now = zone.localize(dt.datetime.now())
    midday = now.replace(hour=12, minute=0, second=0, microsecond=0)
    next_midday = midday + dt.timedelta(days=1)
    ts = load.timescale()
    t0 = ts.from_datetime(midday)
    t1 = ts.from_datetime(next_midday)

    # Setting up Position and Function
    eph = load('de421.bsp')
    position = wgs84.latlon(latitude_degrees = latitude, 
                            longitude_degrees = longitude, 
                            elevation_m = altitude)
    f = almanac.dark_twilight_day(eph, position)
    times, events = almanac.find_discrete(t0, t1, f)

    # Running Function
    sunset_sunrise_times = {}
    previous_e = f(t0).item()

    for t, e in zip(times, events):
        if not e in [3,4]: continue
        if previous_e <= e:
            sunset_sunrise_times[f'{almanac.TWILIGHTS[e]} starts'] = time.mktime(t.astimezone(zone).timetuple())
        else:
            sunset_sunrise_times[f'{almanac.TWILIGHTS[e]} ends'] = time.mktime(t.astimezone(zone).timetuple())
        previous_e = e

    return sunset_sunrise_times
