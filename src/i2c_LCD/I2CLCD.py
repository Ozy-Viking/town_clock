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
lcd.color = [100, 0, 0]
try:
    while True:
        if lcd.left_button:
            lcd.message = "Left!"
            print("Left!")
        elif lcd.right_button:
            lcd.message = "Right!"
            print("Right!")
        elif lcd.up_button:
            lcd.message = "Up!"
            print("Up!")
        elif lcd.down_button:
            lcd.message = "Down!"
            print("Down!")
        elif lcd.select_button:
            lcd.message = "Select!"
            print("Select!")
except KeyboardInterrupt:
    lcd.clear()
    lcd.message = "bye..."
    print('bye...')