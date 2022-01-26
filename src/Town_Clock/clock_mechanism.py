import time

from Town_Clock.clock_logging import Worker
from Town_Clock.clock_data import ClockTime, Diff
from Town_Clock.relay import Clocks, LED
from Town_Clock.clock_enums_exceptions import Mode, PulseError, Clock


class ClockTower:
    def __init__(self, clock_pins, led_pin, mode: Mode = Mode.ACTIVE):
        self.mode = mode
        self.pins = {'Clock': clock_pins, 'LED': led_pin}
        self.clock = Clocks(clock_pins = clock_pins)
        self.led = LED(pin = led_pin)
        self.logger = Worker(name = 'Tower', clock = None)
        self.logger.log('debug', self)

    def __repr__(self):
        return f'ClockTower(pins = {self.pins}, mode = {self.mode})'

    def pulse(self, tm: ClockTime, clock: Clock, mode: Mode = Mode.ACTIVE) -> None:
        self.logger.log('debug','Pulse Method')
        try:
            tm.pulsed = self.clock.pulse(clock = clock)
            tm.clock_time += tm.freq_pulse
            self.clock.pulse_log.log('debug', repr(tm))

        except PulseError as err:
            self.clock.pulse_log.log('error', 'FAILED PULSE')
            self.clock.clocks_log.log('error', f"PulseError: {err}")
            tm.pulsed = False

        except Exception as e:
            self.clock.pulse_log.log('error', 'FAILED PULSE')
            self.clock.clocks_log.log('error', e)
            tm.pulsed = False
        time.sleep(1)
        tm.pulsed = False

    # def input_time(self, clock: Clock) -> float:
    #     self.logger.log('debug','Input Time Method')
    #     # Epoch (0) Thu Jan  1 00:00:00 1970
    #     h = int(input(f'Hour currently on clock {clock}: '))
    #     m = int(input(f'Minute currently on clock {clock}: '))
    #     if h > 12: h += 12
    #     gmt = time.time()
    #     return (gmt-gmt%(60*60*24)) + ((h)*3600 + m*60)

    def check_time_accuracy(self, clocktime: ClockTime, clock: Clock) -> Diff:
        self.logger.log('debug','check_time_accuracy Method')
        clocktime.diff, clocktime.diff_secs = clocktime.clock_time_diff()
        self.logger.log('info',f'{clocktime.diff = }, {clocktime.diff_secs = :.2f}')
        self.time_check_logic(clocktime)

    def time_check_logic(self, ct: ClockTime, clock: Clock = Clock.ALL) -> int:
        self.logger.log('debug','time_check_logic method')
        if ct.diff > 0:       # Fast
            ct.diff_state = Diff.FAST
            self.logger.log('info',"Clock/s is fast")
            self.fast(ct, clock)
        elif ct.diff < 0:     # Slow
            ct.diff_state = Diff.SLOW
            self.logger.log('info',"Clock/s is slow")
            self.slow(ct, clock)
        ct.diff_state = Diff.ON_TIME
        return 

    def fast(self, ct: ClockTime, clock: Clock) -> None:
        # TODO: make 1 clock able to sleep.
        self.logger.log('info',f'Fast: Sleep for {ct.diff_secs:.2f} seconds')
        if clock == Clock.ALL:
            time.sleep(abs(ct.diff_secs))
        elif clock == Clock.ONE:
            pass
        elif clock == Clock.TWO:
            pass

    def slow(self, ct: ClockTime, clock: Clock) -> None:
        self.logger.log('debug',f'Clocktime: {ct}')
        self.logger.log('info',f'Slow: {abs(ct.diff)} pulses')
        for _ in range(abs(ct.diff)):
            self.pulse(ct, clock)
            


if __name__ == '__main__':
    clock_time = ClockTime()
    tower = ClockTower(clock_pins = (12,16), led_pin = 12)
    
