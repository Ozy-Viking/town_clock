"""
relay.py

todo: better error handling
"""
import time

from town_clock.util import *


class Relay:
    """
    Class for relay.
    todo: remember to order of pulses. Alternating between common and clock pin.
    """

    def __init__(
            self, pin: int, name: str, mode: Mode = Mode.TEST
            ) -> None:
        self.mode = mode
        self.pin = pin
        self.name = name

    def single_pulse(self) -> bool:
        try:
            self.turn_on()
            time.sleep(0.1)
            self.turn_off()
            return True
        except Exception as err:
            return False

    def turn_on(self) -> None:
        ...

    def turn_off(self) -> None:
        ...
