from machine import Pin
import utime

led_r = machine.Pin(29, machine.Pin.OUT)
led_y = machine.Pin(28, machine.Pin.OUT)
led_b = machine.Pin(27, machine.Pin.OUT)

while True:
    led_r.toggle()
    led_y.toggle()
    led_b.toggle()
    utime.sleep(1)
