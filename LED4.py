import machine
import utime

pot = machine.ADC(26)
led_r = machine.PWM(machine.Pin(29))
led_y = machine.PWM(machine.Pin(28))
led_b = machine.PWM(machine.Pin(27))
led_r.freq(1000)
led_y.freq(1000)
led_b.freq(1000)

while True:
    led_r.duty_u16(pot.read_u16())
    led_y.duty_u16(pot.read_u16())
    led_b.duty_u16(pot.read_u16())