"""
Todo:
    Add asyncio.
"""
from __future__ import annotations
import os
import sys
import time
from typing import Any  # type: ignore

from icecream import ic

from town_clock.util import *


class Controller:
    """
    Class to control everything.
    """
    __singleton: Controller | None = None

    def __new__(cls, *args, **kwargs):
        """
        Ensures that only one instance of Controller exists.
        """
        if cls.__singleton is None:
            cls.__singleton = super().__new__(cls)
        return cls.__singleton

    def __init__(
            self,
            clock_pins: tuple[int, int],
            led_pin: int,
            common_pin: int,
            lat: float,
            long: float,
            alt: float,
            mode: Mode = Mode.DEV,
            ) -> None:
        self.pins = {
            'common_pin': common_pin,
            'clock_pins': clock_pins,
            'led_pin'   : led_pin,
            }
        self.mode: Mode = mode
        self.position: dict[str, float] = {
            "latitude" : lat,
            "longitude": long,
            "altitude" : alt,
            }

    def run(self) -> None:
        """
        Run the clock computer.
        """
        try:
            while True:
                ic('Controller.run')
                ic(self.__dict__)
                raise KeyboardInterrupt
        except KeyboardInterrupt:
            self.destroy()

    def destroy(self, restart: bool = False) -> None:
        """
        Method to control destruction.

        """

        print("\nbye....")
        sys.exit(0)

    def restart(self, local_time: time.struct_time, force: bool = False) -> None:
        """
        Restart Computer at 2am every day.
        """
        if (local_time.tm_hour == 2 and local_time.tm_min == 0) or force:
            self.destroy(restart=True)
            os.system("sudo init 6")


def get_cpu_temp() -> float:
    """
    Returns the cpu temp when called.

    Todo:
        Fix to work with windows.

    Returns:
        float
    """

    with open("/sys/class/thermal/thermal_zone0/temp") as file:
        cpu = file.read()
    return float(cpu) / 1000
