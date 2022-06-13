import time

from Town_Clock.clock_enums_exceptions import Clock, Mode, PulseError
from Town_Clock.clock_logging import Worker


class Relay:
    def __init__(self, pin: int, name: str, clock: Clock | None, mode: Mode = Mode.ACTIVE):
        self.mode = mode
        self.pin = pin
        self.name = name
        self.relay_log = Worker(name=name, clock=clock)
        self.relay_log.log('debug', repr(self))
        self.__setup()
        self.turn_off()

    def __setup(self) -> None:
        if self.mode == Mode.ACTIVE:
            import RPi.GPIO as GPIO
            GPIO.setwarnings(False)
            GPIO.setup(self.pin, GPIO.OUT)
        else:
            print(f'{self.name} GPIO setup')

    def __repr__(self):
        return (f'Relay(clock pins = {self.pin}, mode = {self.mode},'
                f' Name = {self.name}')

    def single_pulse(self) -> bool:
        try:
            self.turn_on()
            time.sleep(0.1)
            self.turn_off()
            self.relay_log.log('info', f'Pulsed relay: {self.name}')
        except Exception as err:
            self.relay_log.log('error', f'{self.name} error: {err}')
            return False

    def double_pulse(self, clock_relay):
        try:
            self.turn_on()
            clock_relay.turn_on()
            time.sleep(0.1)
            self.turn_off()
            clock_relay.turn_off()
            self.relay_log.log('info', f'Pulsed relay: {self.name} and {clock_relay.name}')
        except Exception as err:
            self.relay_log.log('error', f'{self.name} error: {err}')
            return False

    def turn_on(self):
        if self.mode == Mode.ACTIVE:
            GPIO.output(self.pin, GPIO.LOW)
        # print(f'relay {self.name} on')

    def turn_off(self):
        if self.mode == Mode.ACTIVE:
            GPIO.output(self.pin, GPIO.HIGH)
        # print(f'relay {self.name} off')


class LED(Relay):
    def __init__(self, pin, name='LED', clock=None, mode: Mode = Mode.TEST):
        super().__init__(pin, name, clock, mode=mode)


class Clocks:
    def __init__(self, clock_pins, common_pin, mode: Mode = Mode.TEST):
        self.mode = mode
        self.clocks = {}
        self.clock_pins = clock_pins
        self.clocks[0] = Relay(pin=common_pin,
                               name='Common',
                               clock=None)
        for idx, pin in enumerate(clock_pins):
            self.clocks[idx + 1] = Relay(pin=pin,
                                         name=f'Clock {idx + 1}',
                                         clock=Clock(idx + 1))
        self.qty_clock = len(clock_pins)
        self.pulse_log = Worker(name='Pulse', clock=Clock.ALL)
        self.clocks_log = Worker(name='Clocks', clock=Clock.ALL)
        self.clocks_log.log('debug', repr(self))
        self.direction = {1: 0, 2: 0}

    def __repr__(self):
        return (f'Relay(clock pins = {self.clock_pins}, mode = {self.mode},'
                f' Number of clocks = {self.qty_clock})')

    def pulse(self, clock: Clock | int = Clock.ALL) -> bool | PulseError:
        if clock in Clock.ALL.values:
            clock = Clock(int(clock))
        if type(clock) is not Clock:
            raise PulseError('Did not enter a valid Clock.')

        if clock == Clock.ALL:
            self.pulse_clock(1)
            self.pulse_clock(2)

        elif clock == Clock.ONE:
            self.pulse_clock(1)

        elif clock == Clock.TWO:
            self.pulse_clock(2)

        self.clocks_log.log('info', f'Pulsed {clock}')
        return True

    def pulse_clock(self, clk: int) -> None:
        """
        @param clk: Clock number to Pulse.
        @return:
        """
        if self.direction[clk] == 0:
            self.clocks[clk].single_pulse()
            self.direction[clk] = 1
        else:
            alt_clk = clk % 2 + 1
            self.clocks[0].double_pulse(self.clocks[alt_clk])
            self.direction[clk] = 0


if __name__ == '__main__':
    pass
