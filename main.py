from Town_Clock.clock_controller import Controller


def setup():
    pass


def destroy() -> exit:
    con.destroy()
    exit(0)


if __name__ == '__main__':
    N = E = +1.0
    S = W = -1.0
    # Setup
    clock_pins = 18, 22
    led_pin = 16
    latitude, longitude = 30.3402 * S, 152.7124 * E
    altitude = 741
    
    con = Controller(clock_1_pin = clock_pins[0], 
                     clock_2_pin = clock_pins[1],
                     led_pin = led_pin,
                     lat = latitude, 
                     long = longitude, 
                     alt = altitude
                     )

    # Main loop
    try:
        while True:
            con.main()
    except KeyboardInterrupt:
        destroy()
