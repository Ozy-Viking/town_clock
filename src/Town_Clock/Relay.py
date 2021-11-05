import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)


class ClockPulse:
    def __init__(self, pins: list[int], ) -> None:
        self.pins = pins
        self.setup()

    def setup(self) -> None:
        GPIO.setmode(GPIO.BOARD)       
        for i in self.pins:
            GPIO.setup(i, GPIO.OUT)   
            GPIO.output(i, GPIO.LOW)  

    def pulse(self) -> None:
        for i in self.pins:               
            GPIO.output(i, GPIO.LOW)    # make Pins output LOW level to turn on Relay
        print ('Pulse on')
        time.sleep(0.1)                 # Wait for 1 second
        for i in self.pins:
            GPIO.output(i, GPIO.HIGH)   # make ledPin output HIGH level to turn off Relay
        print ('Pulse off')    

    def destroy(self) -> None:
        GPIO.cleanup()                  # Release all GPIO

if __name__ == '__main__':              # Program entrance
    Pins = [35, 36]                     # use PHYSICAL pin Numbering
    pulse = ClockPulse(Pins)
    try:
        while True:
            pulse.pulse()
            time.sleep(2) 
    except KeyboardInterrupt:           # Press ctrl-c to end the program.
        pulse.destroy()