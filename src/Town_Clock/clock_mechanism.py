import time

from Town_Clock.clock_logging import Worker
from Town_Clock.clock_data import ClockTime
from Town_Clock.relay import Clocks, LED
from Town_Clock.clock_enums_exceptions import Mode, PulseError, Clock
from Town_Clock.location_sunrise_sunset import find_sunrise_sunset_times, timezone_finder


class ClockTower:
    def __init__(self, clock_time: ClockTime, clock_pins: tuple, led_pin, common_pin,
                 position, mode: Mode = Mode.TEST):
        self.mode = mode
        self.clock_time = clock_time
        self.pins = {'Clock': clock_pins, 'LED': led_pin}
        self.clocks = Clocks(clock_pins=clock_pins, common_pin=common_pin, mode=self.mode)
        self.led = LED(pin=led_pin, mode=self.mode)
        self.position = position
        self.logger = Worker(name='Tower', clock=None)
        self.logger.log('debug', repr(self))
        self.next_sunset_sunrise_times = find_sunrise_sunset_times(**self.position)
        for t in self.next_sunset_sunrise_times:
            self.next_sunset_sunrise_times[t] = self.clock_time.mod_freq(tm=self.next_sunset_sunrise_times[t])
        self.timezone = timezone_finder(**self.position)
        self.logger.log('info', f'{self.timezone = }, {self.next_sunset_sunrise_times = }')

    def __repr__(self):
        return f'ClockTower(pins = {self.pins}, mode = {self.mode})'

    def pulse(self, ct: ClockTime, clock_pulses: list[int, int] | None = None) -> None:
        if clock_pulses is None:
            clock_pulses = [0, 0]
        self.logger.log('debug', 'Pulse Method')
        self.clocks.clocks_log.log('info', f'{clock_pulses = }')
        try:
            ct.pulsed = False
            while clock_pulses != [0, 0]:
                if (clock_pulses[0] > 0) and (clock_pulses[1] > 0):
                    ct.pulsed = self.clocks.pulse(clock=Clock.ALL)
                    clock_pulses[0] -= 1
                    clock_pulses[1] -= 1
                    ct.diff = clock_pulses
                    ct.change_clock_time(dt=ct.freq_pulse, clock=Clock.ALL)

                elif clock_pulses[1] == 0:
                    ct.pulsed = self.clocks.pulse(clock=Clock.ONE)
                    clock_pulses[0] -= 1
                    ct.diff = clock_pulses
                    ct.change_clock_time(dt=ct.freq_pulse, clock=Clock.ONE)

                elif clock_pulses[0] == 0:
                    ct.pulsed = self.clocks.pulse(clock=Clock.TWO)
                    clock_pulses[1] -= 1
                    ct.diff = clock_pulses
                    ct.change_clock_time(dt=ct.freq_pulse, clock=Clock.TWO)

                self.clocks.clocks_log.log('info', f'{clock_pulses = }')
                time.sleep(1)

        except PulseError as err:
            self.clocks.clocks_log.log('error', 'FAILED PULSE')
            self.clocks.clocks_log.log('error', f"CM Pulse PulseError: {err}")
            ct.pulsed = False

        except Exception as err:
            self.clocks.clocks_log.log('error', 'FAILED PULSE')
            self.clocks.clocks_log.log('error', f"CM Pulse Exception: {err}")
            ct.pulsed = False

    def check_if_night(self, tm: float) -> None:
        if tm < self.next_sunset_sunrise_times[2]:
            self.logger.log('info', 'Sunrise State 1: LED on')
            self.led.turn_on()
        elif tm < self.next_sunset_sunrise_times[3]:
            self.logger.log('info', 'Sunrise State 2: LED off')
            self.led.turn_off()
        elif self.next_sunset_sunrise_times[3] <= tm < self.next_sunset_sunrise_times[5]:
            self.logger.log('info', 'Sunrise State 3-4: LED on')
            self.led.turn_on()
        elif tm >= self.next_sunset_sunrise_times[5]:
            self.logger.log('info', 'Sunrise State 5: LED off')
            self.led.turn_off()
            self.next_sunset_sunrise_times = find_sunrise_sunset_times(**self.position)
            for t in self.next_sunset_sunrise_times:
                self.next_sunset_sunrise_times[t] = self.clock_time.mod_freq(self.next_sunset_sunrise_times[t])
            self.logger.log('info', f'{self.timezone = }, {self.next_sunset_sunrise_times = }')


if __name__ == '__main__':
    pass
