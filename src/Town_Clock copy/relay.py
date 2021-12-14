from dataclasses import dataclass
import random
import time

from Town_Clock.clock_enums_exceptions import Clock, Mode, PulseError
from Town_Clock.clock_logging import Worker


class Relay:
    def __init__(self, clock_pins, mode:Mode = Mode.TEST):
        self.mode = mode
        self.clock_pins = clock_pins
        self.qty_clock = len(clock_pins)
        self.pulse_log = Worker(name = 'Pulse', clock = Clock.ALL)
        self.relay_log = Worker(name = 'Relay', clock = Clock.ALL)
        self.relay_log.log('debug', self)
        
    def __repr__(self):
        return (f'Relay(clock pins = {self.clock_pins}, mode = {self.mode},'
                f' Number of clocks = {self.qty_clock})')

    def pulse(self, clock: Clock = Clock.ALL) -> bool|PulseError:
        if clock in Clock.ALL.values(): 
            clock = Clock(int(clock))
        if type(clock) is not Clock: 
            raise PulseError('Did not enter a valid Clock.')
        self.relay_log.log('info',f'Pulsed {clock}') # TODO: change to correct formating.
        return True 
           

if __name__ == '__main__':
    pass
