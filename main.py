from Town_Clock import *

if __name__ == "__main__":
    N = E = +1.0
    S = W = -1.0

    clock_pins = 24, 25
    led_pin = 22
    common_pin = 23
    latitude, longitude = 30.3402 * S, 152.7124 * E
    altitude = 741

    controller = Controller(
        clock_pins=clock_pins,
        led_pin=led_pin,
        common_pin=common_pin,
        lat=latitude,
        long=longitude,
        alt=altitude,
        mode=Mode.TEST,
    )

    # Main loop
    while True:
        controller.main()
