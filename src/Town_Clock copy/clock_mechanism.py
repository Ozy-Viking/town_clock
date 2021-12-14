import time

from Town_Clock.clock_logging import Worker
from Town_Clock.clock_data import ClockTime, Diff
from Town_Clock.relay import Clock, Relay, PulseError
from Town_Clock.clock_enums_exceptions import Mode, PulseError


class ClockTower:
    def __init__(self, pins, mode: Mode = Mode.TEST):
        self.pins = pins
        self.relay = Relay(pins)
        self.mode = mode
        self.logger = Worker(name = 'Tower', clock = None)
        self.logger.log('debug', self)

    def __repr__(self):
        return f'ClockTower(pins = {self.pins}, mode = {self.mode})'

    def pulse(self, tm: ClockTime, clock: Clock, mode: Mode = Mode.ACTIVE) -> None:
        self.logger.log('debug','Pulse Method')
        try:
            tm.pulsed = self.relay.pulse()
            tm.clock_time += tm.freq_pulse
            self.relay.pulse_log.log('debug', repr(tm))

        except PulseError as err:
            self.relay.pulse_log.log('error', 'FAILED PULSE')
            self.relay.relay_log.log('error', f"PulseError: {err}")
            tm.pulsed = False

        except Exception as e:
            self.relay.pulse_log.log('error', 'FAILED PULSE')
            self.relay.relay_log.log('error', e)
            tm.pulsed = False

        tm.pulsed = False

    def input_time(self, clock: Clock) -> float:
        self.logger.log('debug','Input Time Method')
        # Epoch (0) Thu Jan  1 00:00:00 1970
        h = int(input(f'Hour currently on clock {clock}: '))
        m = int(input(f'Minute currently on clock {clock}: '))
        if h > 12: h += 12
        gmt = time.time()
        return (gmt-gmt%(60*60*24)) + ((h)*3600 + m*60)

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
            time.sleep(1)


if __name__ == '__main__':
    clock_time = ClockTime()
    tower = ClockTower(pins = (23,24))
