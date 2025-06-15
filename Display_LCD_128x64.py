from machine import Pin
import time

pin_e = Pin(6, Pin.OUT)  # Clock (E)
pin_rw = Pin(5, Pin.OUT)   # Data  (R/W)
pin_rs = Pin(4, Pin.OUT)   # Chip select (RS)

def delay():
    time.sleep_us(72)

def st7920_reset():
    pin_rs.value(0)
    time.sleep_ms(20)
    pin_rs.value(1)
    time.sleep_ms(50)

def st7920_sendbyte(byte):
    for i in range(8):
        pin_rw.value((byte >> (7 - i)) & 1)
        delay()
        pin_e.value(1)
        delay()
        pin_e.value(0)
        delay()

def st7920_write(data, is_data):
    st7920_sendbyte(0xF8 | (0x02 if is_data else 0x00))
    st7920_sendbyte(data & 0xF0)
    st7920_sendbyte((data << 4) & 0xF0)
    time.sleep_us(72)

def st7920_init():
    st7920_reset()
    time.sleep_ms(50)
    st7920_write(0x30, False)
    time.sleep_ms(5)
    st7920_write(0x30, False)
    time.sleep_ms(5)
    st7920_write(0x0C, False)
    time.sleep_ms(5)
    st7920_write(0x01, False)
    time.sleep_ms(5)
    st7920_write(0x06, False)
    time.sleep_ms(5)

def st7920_print(text):
    for c in text:
        st7920_write(ord(c), True)

st7920_init()
st7920_print("RP2040 SPI OK")