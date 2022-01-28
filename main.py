from Town_Clock.clock_controller import Controller        
 
if __name__ == '__main__':        
    N = E = +1.0
    S = W = -1.0
    
    clock_pins = 24, 25
    led_pin = 22
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
    while True:
        con.main()