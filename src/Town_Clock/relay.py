try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError as err:
    exit(1)
import time
from threading import Thread

from Town_Clock.clock_enums_exceptions import Clock, Mode, PulseError
from Town_Clock.clock_logging import Worker

class Relay:
    def __init__(self, pin: int, name: str, clock: Clock|None, mode:Mode = Mode.TEST):
        self.mode = mode
        self.pin = pin
        self.name = name
        self.relay_log = Worker(name = name, clock = clock)
        self.relay_log.log('debug', self)
        self.__setup()
        self.turn_off()

    def __setup(self) -> None:
        GPIO.setwarnings(False)
        GPIO.setup(self.pin, GPIO.OUT)

    def __repr__(self):
        return (f'Relay(clock pins = {self.pin}, mode = {self.mode},'
                f' Name = {self.name}')

    def pulse(self) -> bool:
        pulse = Thread(target = self.__pulse, name = self.name)
        pulse.start()

    def __pulse(self):
        self.turn_on()
        time.sleep(0.1)
        self.turn_off()
        self.relay_log.log('info',f'Pulsed relay: {self.name}')
        return True

    def turn_on(self):
        GPIO.output(self.pin, GPIO.LOW)

    def turn_off(self):
        GPIO.output(self.pin, GPIO.HIGH)


class Clocks:
    def __init__(self, clock_pins, mode:Mode = Mode.TEST):
        self.mode = mode
        self.clocks = {}
        self.clock_pins = clock_pins
        for idx, pin in enumerate(clock_pins):
            self.clocks[f'Clock {idx+1}'] = Relay(pin = pin,
                                                  name = f'Clock {idx+1}', 
                                                  clock = Clock(idx+1))
        self.qty_clock = len(clock_pins)
        self.pulse_log = Worker(name = 'Pulse', clock = Clock.ALL)
        self.clocks_log = Worker(name = 'Clocks', clock = Clock.ALL)
        self.clocks_log.log('debug', self)

    def __repr__(self):
        return (f'Relay(clock pins = {self.clock_pins}, mode = {self.mode},'
                f' Number of clocks = {self.qty_clock})')

    def pulse(self, clock: Clock = Clock.ALL) -> bool|PulseError:
        if clock in Clock.ALL.values(): 
            clock = Clock(int(clock))
        if type(clock) is not Clock:
            raise PulseError('Did not enter a valid Clock.')

        if clock == Clock.ALL:
            for x in self.clocks:
                self.clocks[x].pulse()

        elif clock == Clock.ONE: 
            self.clocks['Clock 1'].pulse()

        elif clock == Clock.TWO:
            self.clocks['Clock 2'].pulse()

        self.clocks_log.log('info',f'Pulsed {clock}')
        return True


class LED(Relay):
    def __init__(self, pin, name = 'LED', clock = None, mode: Mode = Mode.TEST):
        super().__init__(pin, name, clock, mode=mode)


if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    clock = Clocks(clock_pins = (24, 25))
    clock.pulse(clock = Clock.ALL)
    time.sleep(1)
    led = LED(22)
    led.turn_on()
    time.sleep(5)
    led.turn_off()
    pass
