from machine import Pin
import time

pin_e = Pin(6, Pin.OUT)
pin_rw = Pin(5, Pin.OUT)
pin_rs = Pin(4, Pin.OUT)

cmds = [0x30, 0x30, 0x0C, 0x01, 0x06]

class Display:
    def __init__(self):
        self._init_lcd()

    def _reset(self):
        pin_rs.value(0)
        time.sleep_ms(20)
        pin_rs.value(1)
        time.sleep_ms(50)

    def _sendbyte(self, byte):
        for i in range(8):
            pin_rw.value((byte >> (7 - i)) & 1)
            time.sleep_us(72)
            pin_e.value(1)
            time.sleep_us(72)
            pin_e.value(0)
            time.sleep_us(72)

    def _write(self, data, is_data):
        self._sendbyte(0xF8 | (0x02 if is_data else 0x00))
        self._sendbyte(data & 0xF0)
        self._sendbyte((data << 4) & 0xF0)
        time.sleep_us(72)

    def _init_lcd(self):
        self._reset()
        for cmd in cmds:
            self._write(cmd, False)
            time.sleep_ms(5)

    def clear(self):
        self._write(0x01, False)
        time.sleep_ms(2)

    def _set_cursor(self, line):
        addr = [0x80, 0x90, 0x88, 0x98][line % 4]
        self._write(addr, False)

    def print(self, text):
        for c in text:
            self._write(ord(c), True)

    def write_lines(self, lines):
        for i, line in enumerate(lines):
            line_str = "{:<16}".format(str(line)[:16])
            self._set_cursor(i)
            self.print(line_str)

    def center_text(self, text, line):
        padding = max(0, (16 - len(text)) // 2)
        self._set_cursor(line)
        self.print(" " * padding + text)