import machine
import utime

pot = machine.ADC(26)

conversion_factor = 3.3 / 65535

while True:
    voltage = pot.read_u16() * conversion_factor
    print(voltage)
    utime.sleep(0.5)