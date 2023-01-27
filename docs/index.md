# Town Clock

## Overview

## Config

```toml
[Location]
latitude = '30.3402S'
longitude = '152.7124E'
altitude = 741

[Pins]
clock_pins = [24, 25]
led_pin = 22
common_pin = 23

[Mode]
# active, dev, test
mode = 'dev'

[LCD]
lcd_rows = 2
lcd_columns = 16
debounce_sleep = 0.001

[Logging]
# Relative to main package
folder = "logs"
```
