from machine import Pin
import utime

led_r = machine.Pin(29, machine.Pin.OUT)
led_y = machine.Pin(28, machine.Pin.OUT)
led_b = machine.Pin(27, machine.Pin.OUT)
button = machine.Pin(8, machine.Pin.IN, machine.Pin.PULL_UP)

while True:
    if button.value() == 0:
        led_r(1)
        led_y(1)
        led_b(1)
        utime.sleep(0.5)
    led_r(0)
    led_y(0)
    led_b(0)
