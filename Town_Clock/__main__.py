"""
Town-clock
Author: Zack Hankin
Email: zthankin@gmail.com

Config file:
    location: "../config/config.toml"
    contents:
    -----
    [Location]
    latitude =  '30.3402S'
    longitude = '152.7124E'
    altitude = 741

    [Pins]
    clock_pins = [24, 25]
    led_pin = 22
    common_pin = 23
    
    [Mode]
    mode = 'dev', 'test' or 'active'
    ------

"""
import sys

import tomli
from pathlib import Path

from icecream import ic

from town_clock.util import *
from town_clock.controller import Controller

file = Path(__file__, "../../config/config.toml").resolve()

with open(file, "rb") as f:
    config = tomli.load(f)
CONFIG_LOCATION = config["Location"]

latitude = CONFIG_LOCATION["latitude"]
longitude = CONFIG_LOCATION["longitude"]
altitude = CONFIG_LOCATION["altitude"]

latitude = convert_position_string_to_number(latitude)
longitude = convert_position_string_to_number(longitude)

clock_pins = config["Pins"]["clock_pins"]
led_pin = config["Pins"]["led_pin"]
common_pin = config["Pins"]["common_pin"]
mode = Mode(config["Mode"]["mode"])

CONTROLLER = Controller(
    clock_pins=clock_pins,
    led_pin=led_pin,
    common_pin=common_pin,
    lat=latitude,
    long=longitude,
    alt=altitude,
    mode=mode,
    )


def main():
    """
    Function to run project.
    """
    CONTROLLER.run()


if __name__ == '__main__':
    sys.exit(main())
