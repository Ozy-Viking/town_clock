import time
import datetime  # type:ignore

from town_clock.util import *


class ClockTower:
    """
    Todo: needs a rename especially the file
    """

    def __init__(
            self,
            clock_pins: tuple[int, int],
            led_pin: int,
            common_pin: int,
            position: dict[str, float],
            mode: Mode = Mode.ACTIVE,
            ) -> None:
        self.mode = mode
        self.pins = {"Clock": clock_pins, "LED": led_pin}

    def pulse(self, clock_pulses: list[int] | None = None) -> None:
        """
        todo: Keep logic for pulses.
        """
        if clock_pulses is None:
            clock_pulses = [0, 0]
        try:
            while clock_pulses != [0, 0]:
                if (clock_pulses[0] > 0) and (clock_pulses[1] > 0):
                    clock_pulses[0] -= 1
                    clock_pulses[1] -= 1

                elif clock_pulses[1] == 0:
                    clock_pulses[0] -= 1

                elif clock_pulses[0] == 0:
                    clock_pulses[1] -= 1

                time.sleep(1)

        except* PulseError as err:
            ...

    def check_if_night(self, tm: float) -> None:
        """
        Todo: change from int to dict
        """
        ...
