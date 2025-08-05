import psutil
import serial
import serial.tools.list_ports
import threading
import pythoncom
import wmi
import time
import tkinter as tk
from tkinter import messagebox, ttk
import pystray
from PIL import Image, ImageDraw
import pynvml
import logging
import sys
import os

def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

class MonitorSerialApp:
    def __init__(self):
        self.ser = None
        self.icon = None
        self.running = False
        self.interval = 1
        self.port = None
        self.root = tk.Tk()
        icon_path = resource_path("icone.ico")
        self.root.iconbitmap(icon_path)
        self.root.geometry("320x160")
        self.root.title("Hardware Monitor")
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.bind("<Unmap>", self.minimize)
        self.initialize_gui()
        pynvml.nvmlInit()
        self.gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        
    def list_ports(self):
        return [p.device for p in serial.tools.list_ports.comports()]
    
    def connect(self):
        port = self.combo.get()
        if not port:
            messagebox.showerror("Error", "Select a COM port.")
            return
        try:  
            self.ser = serial.Serial(port, 115200, timeout=1)
            self.interval = int(self.freq.get())
            self.running = True
            threading.Thread(target=self.send_data, daemon=True).start()
            self.start_tray()
            self.allow_minimize = True
            logging.info(f"Connected to {port}")
            self.connect_button.config(text="Connected", state="disabled")
            self.disconnect_button.pack()
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")
            logging.error(f"Failed to connect to {port}: {e}")
    
    def disconnect(self):
        self.allow_minimize = False
        self.running = False
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.ser = None
        self.connect_button.config(text="Connect", state="normal")
        self.disconnect_button.pack_forget()
        self.root.update_idletasks()
        self.allow_minimize = False
        logging.info("Disconnected from serial port")
        
    def initialize_gui(self):  
        tk.Label(self.root, text="COM Port:").pack()
        self.combo = ttk.Combobox(self.root, values=self.list_ports())
        self.combo.pack()
        tk.Label(self.root, text="Update Interval (s):").pack()
        self.freq = ttk.Combobox(self.root, values=[str(i) for i in range(1, 61, 5)])
        self.freq.set("1")
        self.freq.pack()
        self.connect_button = tk.Button(self.root, text="Connect", command=self.connect)
        self.connect_button.pack(pady=5)
        self.disconnect_button = tk.Button(self.root, text="Disconnect", command=self.disconnect)
        self.disconnect_button.pack(pady=5)
        self.disconnect_button.pack_forget()

    def start_tray(self):
        if self.icon and self.icon.visible:
            return
        icon_path = resource_path("icone.ico")
        image = Image.open(icon_path)
        menu = pystray.Menu(
            pystray.MenuItem("Show", self.show_window),
            pystray.MenuItem("Exit", self.exit)
        )
        self.icon = pystray.Icon("Monitor", image, "Hardware Monitor", menu)
        threading.Thread(target=self.icon.run, daemon=True).start()
        
    def minimize(self, event=None):
        if not self.allow_minimize:
            return
        if self.ser and self.ser.is_open:
            self.root.withdraw()
            if not self.icon:
                self.start_tray()
            else:
                self.icon.visible = True
        else:
            self.root.iconify()
    
    def close(self):
        self.running = False
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
            except Exception as e:
                logging.error(f"Erro ao fechar porta serial: {e}")
        if self.icon:
            self.icon.stop()
        self.root.destroy()

    def exit(self):
        self.running = False
        if self.ser:
            self.ser.close()
        self.disconnect()  
        self.root.destroy()
        if self.icon:
            self.icon.stop()

    def show_disconnection_error(self):  
        messagebox.showwarning("Disconnected", "Display disconnected!")
        self.allow_minimize = False
        self.connect_button.config(text="Connect", state="normal")
        self.disconnect_button.pack_forget()
        if self.root.state() == "withdrawn":
            self.root.deiconify()
            self.root.lift()

    def show_window(self):  
        self.root.deiconify()
        self.root.after(0, self.root.lift)

    def get_gpu_data(self):
        try:  
            util = pynvml.nvmlDeviceGetUtilizationRates(self.gpu_handle)
            temp = pynvml.nvmlDeviceGetTemperature(self.gpu_handle, pynvml.NVML_TEMPERATURE_GPU)
            power = pynvml.nvmlDeviceGetPowerUsage(self.gpu_handle) // 1000
            fan = pynvml.nvmlDeviceGetFanSpeed(self.gpu_handle)
            return util.gpu, temp, power, fan
        except Exception as e:
            logging.error(f"Error getting GPU data: {e}")
            return 0, 0, 0, 0
  
    def get_disk_usage_percent(self, interval=1.0):
        try:
            c = wmi.WMI()
            for disk in c.Win32_PerfFormattedData_PerfDisk_PhysicalDisk():
                if "C:" in disk.Name:
                    usage = float(disk.PercentDiskTime)
                    return round(min(usage, 100.0), 1)
            return 0.0
        except Exception as e:
            logging.error(f"Error getting SSD data: {e}")
            return 0

    def send_data(self):
        pythoncom.CoInitialize()
        try:
            while self.running:
                try:
                    cpu = psutil.cpu_percent()
                    try:
                        temp_cpu = psutil.sensors_temperatures().get('coretemp', [{}])[0].get('current', 50)
                    except AttributeError:
                        temp_cpu = 50
                    ram = psutil.virtual_memory().percent
                    ssd = self.get_disk_usage_percent()
                    gpu_util, gpu_temp, gpu_watts, gpu_fan = self.get_gpu_data()
                    lines = [
                        f"CPU:{int(cpu)}% {int(temp_cpu)}C",
                        f"RAM:{int(ram)}% SSD:{int(ssd)}%",
                        f"GPU:{gpu_util}% {gpu_temp}C {gpu_watts}W",
                        f"Fan:{int(gpu_fan / 100 * 1700)} RPM"
                    ]
                    if self.ser and self.ser.is_open:
                        self.ser.write(("\n".join(lines) + "\n").encode('ascii'))
                    else:  
                        logging.warning("Serial port is not open")
                except Exception as e:
                    self.running = False
                    if self.ser:
                        self.ser.close()
                    self.ser = None
                    self.show_disconnection_error()
                    logging.error(f"Error sending data: {e}")
                    break
                time.sleep(self.interval)
        finally:
            pythoncom.CoUninitialize()
    
    def run(self):  
        self.root.mainloop()

if __name__ == "__main__":
    app = MonitorSerialApp()
    app.run()