# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""Simple test for I2C RGB character LCD shield kit"""
import time
import board
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd

# Modify this if you have a different sized Character LCD
lcd_columns = 16
lcd_rows = 2

# Initialise I2C bus.
i2c = board.I2C()  # uses board.SCL and board.SDA

# Initialise the LCD class
lcd = character_lcd.Character_LCD_RGB_I2C(i2c, lcd_columns, lcd_rows)

lcd.clear()
# Backlight
lcd.color = [0, 0, 0]
lcd.color = [100, 0, 0]


class Buttons:
    @property
    def Up(self) -> bool:
        return lcd.up_button
    
    @property
    def Down(self) -> bool:
        return lcd.down_button
    
    @property
    def Left(self) -> bool:
        return lcd.left_button
    
    @property
    def Right(self) -> bool:
        return lcd.right_button
    
    @property
    def Select(self) -> bool:
        return lcd.select_button

    @property
    def buttons(self) -> dict:
        return {'Up': lcd.up_button,
                'Down': lcd.down_button,
                'Left': lcd.left_button,
                'Right': lcd.right_button,
                'Select': lcd.select_button
                }  

buttons = Buttons()
# print(buttons.Select)

# def press_button(btn: str) -> None:
#     while buttons.__getattribute__(btn):
#         time.sleep(0.1)
        
# for btn in buttons.buttons.keys():
#     if buttons.__getattribute__(btn):
#         print(btn)
#         press_button(btn)
# print('done')

# print(lcd.__dir__())

def check_button_pressed() -> str:
    pressed_buttons = buttons.buttons
    for btn in pressed_buttons.keys():
        if pressed_buttons[btn]:
            print(btn)
            # press_button(btn)
            return btn
    return None


def press_button(btn: str) -> None:
    while buttons.__getattribute__(btn):
        time.sleep(0.01)

def write_to_screen_center(line_1:str, line_2:str) -> None:
    t0 = time.perf_counter()
    start_1 = (16 - len(line_1))//2
    start_2 = (16 - len(line_2))//2
    t1 = time.perf_counter()
    space_1 = ' ' * (start_1)
    space_2 = ' ' * (start_2)
    t2 = time.perf_counter()
    lcd.message = (f'{space_1}{line_1}{space_1}\n'
                   f'{space_2}{line_2}{space_2}' )   # display the time 
    t3 = time.perf_counter()
    print (f'Total {t3-t0:02f}')
    print (t1-t0)
    print (t2-t1)
    print (t3-t2)

try:
    while True: # 2,929,112 3,510,168
        t0 = time.perf_counter()
        btn = check_button_pressed()
        if btn:
            write_to_screen_center(btn,'Button')
            # print(f"{btn}\ntext")
        # elif buttons.Right:
        #     lcd.message = "Right!"
        #     print("Right!")
        # elif buttons.Up:
        #     lcd.message = "Up"
        #     print("Up!")
        # elif buttons.Down:
        #     lcd.message = "Down!"
        #     print("Down!")
        # elif buttons.Select:
        #     lcd.message = "Select!"
        #     print("Select!")
            t1 = time.perf_counter()
            print(t1-t0)
except KeyboardInterrupt:
    lcd.clear()
    lcd.message = "bye..."
    print('bye...')
    