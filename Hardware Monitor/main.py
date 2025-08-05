from display import Display
import sys
import time
import select

# Inicializa o display
lcd = Display()
lcd.clear()
lcd.center_text(" DISCONNECTED!", line=1)

last_data = time.ticks_ms()
receiving = False

buffer = []

try:
    while True:
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            line = sys.stdin.readline().strip()
            if line:
                buffer.append(line[:16])
                if len(buffer) == 4:
                    if not receiving:
                        lcd.clear()
                        lcd.center_text("SYNC...", line=1)
                        time.sleep(1)
                        lcd.clear()
                        receiving = True
                    lcd.write_lines(buffer)
                    buffer = []
                    last_data = time.ticks_ms()
        else:
            if receiving and time.ticks_diff(time.ticks_ms(), last_data) > 5000:
                lcd.clear()
                lcd.center_text(" DISCONNECTED!", line=1)
                receiving = False
except Exception as e:
    lcd.clear()
    lcd.center_text("SYSTEM ERROR", line=1)