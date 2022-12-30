#!/usr/bin/env python3
import time  # type: ignore
from datetime import datetime  # type: ignore
from multiprocessing import Queue, Event
from typing import Any, Optional  # type: ignore
import board  # type: ignore
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd  # type: ignore

from Town_Clock import *

# todo: Check types and remove ignore tags/Any types.


class Buttons:
    @property
    def Up(self) -> bool:
        return LCD.up_button

    @property
    def Down(self) -> bool:
        return LCD.down_button

    @property
    def Left(self) -> bool:
        return LCD.left_button

    @property
    def Right(self) -> bool:
        return LCD.right_button

    @property
    def Select(self) -> bool:
        return LCD.select_button

    @property
    def buttons(self) -> dict[str, Any]:
        return {
            "Up": LCD.up_button,
            "Down": LCD.down_button,
            "Left": LCD.left_button,
            "Right": LCD.right_button,
            "Select": LCD.select_button,
        }


def time_now() -> str:  # get system time
    return datetime.now().strftime("%H:%M:%S")


def get_title(c: int) -> str:
    if not c:
        return "Both Clocks"
    return f"Clock {c}"


def go_to_sleep(logger: Worker) -> float:
    logger.log(20, "LCD sleeping")
    LCD.color = [0, 0, 0]  # turn on LCD backlight
    LCD.clear()
    while True:
        # print('Sleeing')
        time.sleep(0.5)
        if check_button_pressed():  # if button is pressed
            break

    LCD.color = [100, 0, 0]
    logger.log(20, "LCD Waking Up")
    return time.time()


def check_button_pressed() -> str | None:
    pressed_buttons = buttons.buttons
    for btn, val in pressed_buttons.items():
        if val:
            press_button(btn)
            return btn
    return None


def press_button(btn: str) -> None:
    while buttons.__getattribute__(btn):
        time.sleep(0.0001)


def cpu_temp_and_time() -> str:
    print_time: str = time_now()
    cpu: float = get_cpu_temp()
    return f" {print_time}  {round(cpu)} C "


def write_to_screen_center(line_1: str, line_2: str) -> None:
    LCD.cursor_position(0, 0)
    start_1 = (16 - len(line_1)) // 2
    start_2 = (16 - len(line_2)) // 2
    space_1 = " " * start_1
    space_2 = " " * start_2
    LCD.message = f"{space_1}{line_1}{space_1}\n" f"{space_2}{line_2}{space_2}"


def change_clock_value(clock: int, queue: Queue, event: Event, logger: Worker) -> None:  # type: ignore
    tm = time.time() // 1
    tm1 = tm

    LCD.cursor = True
    press = None
    cursor_index = 0
    valid_positions = [5, 4, 2, 1]  # Position
    amount = [60, 60 * 10, 60**2, 60**2 * 10]  # Amount to add or subtract

    while True:
        write_to_screen_center(
            f"Clock {clock} shows",
            f"{str(change_time_to_print(tm))} -> {change_time_to_print(tm1)}",
        )
        LCD.cursor_position(valid_positions[cursor_index], 1)
        while press is None:
            press = check_button_pressed()
        if press == "Up":
            tm += amount[cursor_index]
        elif press == "Down":
            tm -= amount[cursor_index]
        elif press == "Left":
            cursor_index = (cursor_index + 1) % 4
        elif press == "Right":
            cursor_index = (cursor_index - 1) % 4
        elif press == "Select":
            break

        press = None
        time.sleep(debounce_sleep)

    LCD.cursor = False
    write_to_screen_center(
        f"Changing Clock {clock}\n",
        f"{change_time_to_print(tm)} -> {change_time_to_print()}",
    )
    event.set()  # type: ignore

    # If clock shows a time ahead of the current time, this will be positive.
    diff = int((tm - tm1) // 60)
    queue.put((clock, diff))  # type: ignore
    logger.log("info", f"Putting {clock = }, {diff = } on queue")
    logger.log("info", f"Difference: {diff}")
    print(f"Difference: {diff}")
    time.sleep(2)


def change_time_to_print(tm: Optional[float] = None) -> str:  # get system time
    if tm is None:
        tm = time.time()
    return datetime.fromtimestamp(tm).strftime("%H:%M")


def loop(screen_queue: Queue, input_event: Event, logger: Worker) -> None:  # type: ignore
    LCD.clear()
    LCD.color = [100, 0, 0]  # turn on LCD backlight
    change_clock = False
    c = 0
    last_time_button_pressed = time.time()
    write_to_screen_center(cpu_temp_and_time(), get_title(c))
    while True:
        try:
            btn = check_button_pressed()
            if btn is None:
                pass
            elif btn == "Select":
                last_time_button_pressed = go_to_sleep(logger)

            elif btn == "Left":
                c -= 1
                c = c % 3
                change_clock = True

            elif btn == "Right":
                c += 1
                c = c % 3
                change_clock = True

            elif btn == "Up" or btn == "Down":
                logger.log(20, f"Inputting time on clock {c}")
                change_clock_value(
                    clock=c, queue=screen_queue, event=input_event, logger=logger  # type: ignore
                )

                LCD.clear()

            if btn:
                last_time_button_pressed = time.time()

            td = time.time() - last_time_button_pressed
            if td >= 60 * 5:  # Sleep after 5 min.
                last_time_button_pressed = go_to_sleep(logger=logger)

            if int((time.time() * 10) % 10) == 0 or change_clock:
                write_to_screen_center(cpu_temp_and_time(), get_title(c))

        except KeyboardInterrupt:
            destroy()
        except Exception as err:
            logger.log("error", f"LCD Error: {err}", name="LCD")


def destroy() -> None:
    write_to_screen_center("Goodbye.....", " ")
    time.sleep(1)
    LCD.color = [0, 0, 0]  # turn off LCD backlight
    LCD.clear()


def setup() -> None:
    pass


def main(screen_queue: Queue, input_event: Event, logger: Worker) -> None:  # type: ignore
    logger.log(10, "Starting main")

    # Modify this if you have a different sized Character LCD
    lcd_columns = 16
    lcd_rows = 2

    # Initialise I2C bus.
    i2c: Any = board.I2C()  # type: ignore # uses board.SCL and board.SDA

    # Initialise the LCD class
    global LCD
    LCD: Any = character_lcd.Character_LCD_RGB_I2C(i2c, lcd_columns, lcd_rows)  # type: ignore
    logger.log(10, "LCD object made")

    global debounce_sleep
    debounce_sleep = 0.001

    global buttons
    buttons = Buttons()

    setup()
    logger.log(10, "LCD object made")
    logger.log(10, "LCD loop about to start")
    loop(screen_queue, input_event, logger)  # type: ignore


def get_cpu_temp() -> float:
    with open("/sys/class/thermal/thermal_zone0/temp") as file:
        cpu = file.read()
    return float(cpu) // 1000


if __name__ == "__main__":
    pass
