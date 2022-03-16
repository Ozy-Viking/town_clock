#!/usr/bin/env python3
import time
from datetime import datetime
from multiprocessing import Queue, Event
import board
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd

from Town_Clock.clock_logging import Worker


class Buttons:
    @property
    def up(self) -> bool:
        return lcd.up_button

    @property
    def down(self) -> bool:
        return lcd.down_button

    @property
    def left(self) -> bool:
        return lcd.left_button

    @property
    def right(self) -> bool:
        return lcd.right_button

    @property
    def select(self) -> bool:
        return lcd.select_button

    @property
    def buttons(self):
        return {'Up': lcd.up_button,
                'Down': lcd.down_button,
                'Left': lcd.left_button,
                'Right': lcd.right_button,
                'Select': lcd.select_button
                }


def time_now():  # get system time
    return datetime.now().strftime('%H:%M:%S')


def get_title(c: int) -> str:
    if not c:
        return 'Both Clocks'
    return f'Clock {c}'


def go_to_sleep(logger: Worker) -> float:
    logger.log(20, 'LCD sleeping')
    lcd.color = [0, 0, 0]  # turn on LCD backlight
    lcd.clear()
    while True:
        # print('Sleeing')
        time.sleep(0.5)
        if check_button_pressed():  # if button is pressed
            break

    lcd.color = [100, 0, 0]
    logger.log(20, 'LCD Waking Up')
    return time.time()


def check_button_pressed() -> str:
    pressed_buttons = buttons.buttons
    for btn, val in pressed_buttons.items():
        if val:
            press_button(btn)
            return btn
    return None


def press_button(btn: str) -> None:
    while buttons.__getattribute__(btn):
        time.sleep(0.0001)


def write_to_screen_center(line_1: str, line_2: str) -> None:
    lcd.cursor_position(0, 0)
    start_1 = (16 - len(line_1)) // 2
    start_2 = (16 - len(line_2)) // 2
    space_1 = ' ' * start_1
    space_2 = ' ' * start_2
    lcd.message = (f'{space_1}{line_1}{space_1}\n'
                   f'{space_2}{line_2}{space_2}')  # display the time


def change_clock_value(clock: int, queue: Queue, event: Event, logger: Worker):
    tm = time.time() // 1
    tm1 = tm

    lcd.cursor = True
    press = None
    p = 0
    cursor = [5, 4, 2, 1]  # Position
    amount = [60, 60 * 10, 60 ** 2, 60 ** 2 * 10]  # Amount to add or subtract

    while True:
        write_to_screen_center(f'Clock {clock} shows',
                               f'{str(change_time_to_print(tm))} -> {change_time_to_print(tm1)}')
        lcd.cursor_position(cursor[p], 1)
        while press is None:
            press = check_button_pressed()
        if press == 'Up':
            tm += amount[p]
        elif press == 'Down':
            tm -= amount[p]
        elif press == 'Left':
            p = (p + 1) % 4
        elif press == 'Right':
            p = (p - 1) % 4
        elif press == 'Select':
            break

        press = None
        time.sleep(debounce_sleep)

    lcd.cursor = False
    write_to_screen_center(f'Changing Clock {clock}\n',
                           f'{change_time_to_print(tm)} -> {change_time_to_print()}')
    event.set()

    # If clock shows a time ahead of the current time, this will be positive.
    diff = int((tm - tm1) // 60)
    queue.put((clock, diff))
    logger.log('info', f'Putting {clock = }, {diff = } on queue')
    logger.log('info', f'Difference: {diff}')
    print(f'Difference: {diff}')
    time.sleep(2)


def change_time_to_print(tm: float = None):  # get system time
    if tm is None:
        tm = time.time()
    return datetime.fromtimestamp(tm).strftime('%H:%M')


def loop(screen_queue: Queue, input_event: Event, logger: Worker):
    lcd.clear()
    lcd.color = [100, 0, 0]  # turn on LCD backlight
    change_clock = False
    c = 0
    last_time_button_pressed = time.time()
    write_to_screen_center(get_title(c), time_now())
    while True:
        btn = check_button_pressed()
        if btn is None:
            pass
        elif btn == 'Select':
            last_time_button_pressed = go_to_sleep(logger)

        elif btn == 'Left':
            c -= 1
            c = c % 3
            change_clock = True

        elif btn == 'Right':
            c += 1
            c = c % 3
            change_clock = True

        elif btn == 'Up' or btn == 'Down':
            logger.log(20, f'Inputting time on clock {c}')
            change_clock_value(clock=c,
                               queue=screen_queue,
                               event=input_event,
                               logger=logger)

            lcd.clear()

        if btn:
            last_time_button_pressed = time.time()

        td = time.time() - last_time_button_pressed
        if td >= 60 * 5:  # Sleep after 5 min.
            last_time_button_pressed = go_to_sleep(logger=logger)

        if int((time.time() * 10) % 10) == 0 or change_clock:
            write_to_screen_center(get_title(c), time_now())


def destroy():
    write_to_screen_center('Goodbye.....', ' ')
    time.sleep(1)
    lcd.color = [0, 0, 0]  # turn off LCD backlight
    lcd.clear()


def setup():
    pass


def main(screen_queue: Queue, input_event: Event, logger: Worker):
    logger.log(10, 'Starting main')

    # Modify this if you have a different sized Character LCD
    lcd_columns = 16
    lcd_rows = 2

    # Initialise I2C bus.
    i2c = board.I2C()  # uses board.SCL and board.SDA

    # Initialise the LCD class
    global lcd
    lcd = character_lcd.Character_LCD_RGB_I2C(i2c, lcd_columns, lcd_rows)
    logger.log(10, 'LCD object made')

    global debounce_sleep
    debounce_sleep = 0.001

    global buttons
    buttons = Buttons()

    setup()
    logger.log(10, 'LCD object made')
    try:
        logger.log(10, 'LCD loop about to start')
        loop(screen_queue, input_event, logger)
    except KeyboardInterrupt:
        destroy()
    except Exception as err:
        print(err)
        destroy()


if __name__ == '__main__':
    pass
