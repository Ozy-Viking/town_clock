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
    def __init__(self, clock_pins, common_pin, mode:Mode = Mode.TEST):
        self.mode = mode
        self.clocks = {}
        self.clock_pins = clock_pins
        self.clocks[0] = Relay(pin = common_pin,
                                                  name = 'Common', 
                                                  clock = None)
        for idx, pin in enumerate(clock_pins):
            self.clocks[idx+1] = Relay(pin = pin,
                                                  name = f'Clock {idx+1}', 
                                                  clock = Clock(idx+1))
        self.qty_clock = len(clock_pins)
        self.pulse_log = Worker(name = 'Pulse', clock = Clock.ALL)
        self.clocks_log = Worker(name = 'Clocks', clock = Clock.ALL)
        self.clocks_log.log('debug', self)
        self.direction = 0

    def __repr__(self):
        return (f'Relay(clock pins = {self.clock_pins}, mode = {self.mode},'
                f' Number of clocks = {self.qty_clock})')

    def pulse(self, clock: Clock = Clock.ALL) -> bool|PulseError:
        if clock in Clock.ALL.values(): 
            clock = Clock(int(clock))
        if type(clock) is not Clock:
            raise PulseError('Did not enter a valid Clock.')

        if clock == Clock.ALL:
            if self.direction == 0:
                self.direction +=1
                self.clocks[1].pulse()
                self.clocks[2].pulse()
            elif self.direction == 1:
                self.direction -=1
                self.clocks[0].pulse()

        elif clock == Clock.ONE: 
            if self.direction == 0:
                self.direction +=1
                self.clocks[1].pulse()
            elif self.direction == 1:
                self.direction -=1
                self.clocks[2].pulse()
                self.clocks[0].pulse()

        elif clock == Clock.TWO:
            if self.direction == 0:
                self.direction +=1
                self.clocks[2].pulse()
            elif self.direction == 1:
                self.direction -=1
                self.clocks[1].pulse()
                self.clocks[0].pulse()

        self.clocks_log.log('info',f'Pulsed {clock}')
        time.sleep(0.1)
        return True


class LED(Relay):
    def __init__(self, pin, name = 'LED', clock = None, mode: Mode = Mode.TEST):
        super().__init__(pin, name, clock, mode=mode)


if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    clock = Clocks(clock_pins = (24, 25), common_pin= 23)
    led1 = LED(24)
    led2 = LED(25)
    for x in range(1):
        clock.pulse(Clock.TWO)
        print(x)
        time.sleep(1)
    # clock.pulse(Clock.ONE)
    # time.sleep(2)
    # clock.pulse(Clock.ONE)
    # time.sleep(2)
        # clock.pulse(Clock.ALL)
        # time.sleep(2)
        # clock.pulse(Clock.ALL)
        # time.sleep(2)
        # clock.pulse(Clock.ALL)
        # time.sleep(2)
        # clock.pulse(Clock.ALL)
        # time.sleep(2)
        # led1.turn_on()
        # led2.turn_on()
        # time.sleep(5)
        # led1.turn_off()
        # led2.turn_off()
        # time.sleep(5)
    # led = LED(22)
    # led.turn_on()
    # time.sleep(30)
    # led.turn_off()
    pass
