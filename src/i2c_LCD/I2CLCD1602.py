#!/usr/bin/env python3
import time
from datetime import datetime
from enum import Enum
from multiprocessing import Queue, Event

from i2c_LCD.Adafruit_LCD1602 import Adafruit_CharLCD
from i2c_LCD.PCF8574 import PCF8574_GPIO

from Town_Clock.clock_logging import Worker

try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError as err:
    exit(1)

def time_now():     # get system time
    return datetime.now().strftime('%H:%M:%S')


def get_title(c):
    if not c: return 'Both Clocks'
    return f'Clock {c}'


def go_to_sleep(logger: Worker):
    logger.log('info', 'LCD sleeping')
    mcp.output(3,0)     # turn on LCD backlight
    lcd.clear()
    while True:
        # print('Sleeping')
        time.sleep(0.5)
        if check_button_pressed(): # if button is pressed
            break
            
    mcp.output(3,1)
    logger.log('info', 'LCD Waking Up')
    return time.time()


def check_button_pressed() -> dict | bool:
    for pin in button_pins:
        if GPIO.input(button_pins[pin]) == GPIO.LOW:
            press_button(button_pins[pin])
            return pin
    return None


def press_button(button_pin: int) -> None:
    while GPIO.input(button_pin) == GPIO.LOW:
        time.sleep(debounce_sleep)


def write_to_screen_center(line_1:str, line_2:str) -> None:
    start_1 = (16 - len(line_1))//2
    start_2 = (16 - len(line_2))//2
    space_1 = ' ' * (start_1)
    space_2 = ' ' * (start_2)
    lcd.setCursor(0,0)  # set cursor position
    lcd.message( f'{space_1}{line_1}{space_1}' )   # display the time
    lcd.setCursor(0,1)  # set cursor position
    lcd.message( f'{space_2}{line_2}{space_2}' )   # display the time 


def change_clock_value(clock: int, queue: Queue, event: Event, logger: Worker):
    tm = time.time()//1
    tm1 = tm

    lcd.cursor()
    press = None
    p = 0
    cursor = [5, 4, 2, 1] # Postion
    amount = [60, 60*10, 60**2, 60**2*10] # Amount to add or subtract

    while True:
        write_to_screen_center(f'Clock {clock} shows', f'{str(change_time_to_print(tm))} -> {change_time_to_print(tm1)}')
        lcd.setCursor(cursor[p],1)
        while press is None:
            press = check_button_pressed()
        if press == 'add_1':
            tm += amount[p]
        elif press == 'sub_1':
            tm -= amount[p]
        elif press == 'left':
            p = (p + 1) % 4
        elif press == 'right':
            p = (p - 1) % 4
        elif press == 'select':
            break

        press = None
        time.sleep(debounce_sleep)

    lcd.noCursor()
    write_to_screen_center(f'Changing Clock {clock}', f'{str(change_time_to_print(tm))} -> {change_time_to_print()}')
    event.set()
    diff = int((tm1-tm)//60)
    queue.put(clock,diff)
    logger.log('debug', f'Putting {tm = }, {tm1 = } on queue')
    logger.log('debug', f'Difference: {diff}')
    time.sleep(2)


def change_time_to_print(tm: float = None):     # get system time
    if tm is None: tm = time.time()
    return datetime.fromtimestamp(tm).strftime('%H:%M')


def loop(screen_queue: Queue, input_event: Event, logger: Worker):
    lcd.begin(16,2)     # set number of LCD lines and columns
    lcd.clear()
    mcp.output(3,1)     # turn on LCD backlight
    change_clock = False
    c = 0
    last_time_button_pressed = time.time() 
    write_to_screen_center(get_title(c), time_now())
    while True:         
        pin = check_button_pressed()
        match pin:
            case None: pass
            case 'select': last_time_button_pressed = go_to_sleep(logger)
            
            case 'left': 
                c -= 1
                c = c % 3
                change_clock = True
            
            case 'right':
                c += 1
                c = c % 3
                change_clock = True
            
            case 'add_1'|'sub_1':
                logger.log('info', f'Inputing time on clock {c}')
                change_clock_value(clock = c, 
                                   queue = screen_queue, 
                                   event = input_event,
                                   logger = logger)
                
                lcd.clear()

        if pin: last_time_button_pressed = time.time()

        td = time.time() - last_time_button_pressed
        if td >= 60*5:                                 # Sleep after 5 min.
            last_time_button_pressed = go_to_sleep(logger = logger)  

        if int((time.time()*10)%10) == 0 or change_clock:
            write_to_screen_center(get_title(c), time_now())

        time.sleep(debounce_sleep)


def destroy():
    write_to_screen_center('Goodbye.....',' ')
    time.sleep(1)
    mcp.output(3,0)     # turn off LCD backlight
    lcd.clear()


def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD) # use PHYSICAL GPIO Numbering
    for pin in button_pins:
        GPIO.setup(button_pins[pin], GPIO.IN, pull_up_down=GPIO.PUD_UP) # set buttonPin to PULL UP INPUT mode


def main(screen_queue: Queue, input_event: Event, logger: Worker):
    logger.log('debug', 'Starting main')
    PCF8574_address = 0x27  # I2C address of the PCF8574 chip.
    # Create PCF8574 GPIO adapter.
    global mcp
    try:
        mcp = PCF8574_GPIO(PCF8574_address)
    except:
        logger.log('error', 'I2C Address Error !')
        exit(1)
        
    # Create LCD, passing in MCP GPIO adapter.
    global lcd
    lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=mcp)
    logger.log('debug','LCD object made')

    global debounce_sleep
    debounce_sleep = 0.001

    global button_pins
    button_pins = {
        'right': 36,
        'left': 37,
        'add_1': 38,
        'sub_1': 40,
        'select': 26
    }
    
    global change_time_buttons
    change_time_buttons = ['add_1','sub_1','left','right']
    setup()
    logger.log('debug','LCD object made')
    try:
        logger.log('debug','LCD loop about to start')
        loop(screen_queue, input_event, logger)
    except KeyboardInterrupt:
        destroy()
    except Exception as err:
        print(err)
        destroy()
