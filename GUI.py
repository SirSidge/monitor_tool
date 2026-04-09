import customtkinter as ctk
from pystray import MenuItem, Icon, Menu
from PIL import Image
import threading
import time
from datetime import date
import psutil
import ctypes
from ctypes import wintypes, Structure, windll, c_uint, sizeof, byref
import json
from pathlib import Path
import os

class LASTINPUTINFO(Structure):
    _fields_ = [
        ('cbSize', c_uint),
        ('dwTime', c_uint),
    ]

class MonitorToolUI:
    def __init__(self, minimize_on_start=True):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.root = ctk.CTk()
        self.root.geometry("800x640")
        self.root.title("Monitor Tool")
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        # Variables
        self._valid_states = {
            "productive": {"Code.exe"},
            "unproductive": {"PathOfExile.exe", "Balls.exe"},
            "idle": {},
        }
        self.productivity_state = "idle"
        self.window_visible = True
        self.last_stat_update = time.time()
        self.inactive = False
        self.file_path = Path(r'C:\monitoring tool - temp data\running_data.json')
        self.running_data = {
            "metadata": {
                "last_active_date": date.today().isoformat()
            },
            "stats": {
                "day": {
                    "productive": 0,
                    "unproductive": 0,
                    "idle": 0
                },
                "month": {
                    "productive": 0,
                    "unproductive": 0,
                    "idle": 0
                },
                "total": {
                    "productive": 0,
                    "unproductive": 0,
                    "idle": 0
                }
            }
        }
        self.last_active = date.today()
        self.icon = Icon("my_app")
        self.taskbar_icons = {
            "idle": Image.new('RGB', (64, 64), color = 'black'),
            "productive": Image.new('RGB', (64, 64), color = 'green'),
            "unproductive": Image.new('RGB', (64, 64), color = 'red'),
            }
        self.icon.icon = self.taskbar_icons[self.productivity_state]
        self.icon.menu=Menu(
            MenuItem('Show', self.show_window),
            MenuItem('Quit', self.quit_app)
        )
        self.icon_thread = threading.Thread(target=self.icon.run, daemon=True)
        self.icon_thread.start()
        # Frame and widgets
        self.frame = ctk.CTkFrame(self.root, fg_color="gray20", corner_radius=10)
        self.frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.stats_label = ctk.CTkLabel(self.frame, text="-- initialising --")
        self.stats_label.grid(row=0, column=0, padx=10, pady=10)
        self.processes_button = ctk.CTkButton(self.frame, text="Quit", command=self.quit_app)
        self.processes_button.grid(row=1, column=0, padx=10, pady=10)
        self.stats_day = ctk.CTkLabel(self.frame, text="-- initialising --")
        self.stats_day.grid(row=0, column=1, padx=10, pady=10)
        self.stats_month = ctk.CTkLabel(self.frame, text="-- initialising --")
        self.stats_month.grid(row=0, column=3, padx=10, pady=10)
        self.stats_total = ctk.CTkLabel(self.frame, text="-- initialising --")
        self.stats_total.grid(row=0, column=4, padx=10, pady=10)
        # Minimize on Start (Note: Needs to stay at end of __init__ to avoid interrupting the building of the app.)
        if minimize_on_start:
            self.root.after(2000, self.hide_window)

    def set_status(self, state):
        print(state)
        if state in self._valid_states.keys():
            current_time = time.time()
            self.running_data["stats"]["day"][self.productivity_state] += current_time - self.last_stat_update
            self.running_data["stats"]["month"][self.productivity_state] += current_time - self.last_stat_update
            self.running_data["stats"]["total"][self.productivity_state] += current_time - self.last_stat_update
            self.last_stat_update = current_time
            self.productivity_state = state
            self.update_taskbar_icon()
        else:
            raise ValueError(f"Invalid state: {state}")
        
    def auto_update_stats(self):
        print("Saving...")
        obj_json = json.dumps(self.running_data, indent=4)
        with open(self.file_path, 'w') as f:
            f.write(obj_json)
        self.root.after(20000, self.auto_update_stats)
    
    def quit_app(self):
        self.save_to_file()
        self.icon.stop()
        self.root.destroy()

    def show_window(self):
        self.root.deiconify()
        self.window_visible = True
        self.draw()
        self.draw_infrequent()

    def hide_window(self):
        self.root.withdraw()
        self.window_visible = False

    def open_file(self):
        if not os.path.exists(self.file_path):
            print("File not found, creating new file...")
            self.save_to_file()
            return
        print("File opening...")
        with open(self.file_path, "r", encoding='utf-8') as f:
            self.running_data = json.load(f)
            if "metadata" not in self.running_data:
                self.running_data["metadata"] = {"last_active_date": date.today().isoformat()}

    def save_to_file(self):
        obj_json = json.dumps(self.running_data, indent=4)
        with open(self.file_path, 'w') as f:
            f.write(obj_json)

    def update_taskbar_icon(self):
        self.icon.icon = self.taskbar_icons[self.productivity_state]

    def get_foreground_process_name(self):
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if hwnd == 0:
            return None
        pid = wintypes.DWORD()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value == 0:
            return None
        try:
            process = psutil.Process(pid.value)
            return process.name()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
        
    def determine_state(self):
        if not self.inactive:
            foreground_app = self.get_foreground_process_name()
            for k, v in self._valid_states.items():
                if foreground_app in v:
                    self.set_status(k)
                    break
            else:
                self.set_status("idle")
        else:
            self.set_status("idle")

    def get_idle_duration(self):
        lastInputInfo = LASTINPUTINFO()
        lastInputInfo.cbSize = sizeof(lastInputInfo)
        windll.user32.GetLastInputInfo(byref(lastInputInfo))
        sec = (windll.kernel32.GetTickCount64() - lastInputInfo.dwTime) / 1000
        if sec >= 300:
            self.inactive = True
        else:
            self.inactive = False
    
    def check_date(self):
        if date.fromisoformat(self.running_data["metadata"]["last_active_date"]).month != date.today().month:
            self.running_data["stats"]["month"]["productive"] = 0
            self.running_data["stats"]["month"]["unproductive"] = 0
            self.running_data["stats"]["month"]["idle"] = 0
            self.draw_infrequent()
        if self.running_data["metadata"]["last_active_date"] != date.today().isoformat():
            self.running_data["stats"]["day"]["productive"] = 0
            self.running_data["stats"]["day"]["unproductive"] = 0
            self.running_data["stats"]["day"]["idle"] = 0
            self.running_data["metadata"]["last_active_date"] = date.today().isoformat()
            self.draw_infrequent()
        self.root.after(1500, self.check_date)

    def draw(self):
        if self.window_visible:
            self.stats_label.configure(text=f"{self.productivity_state}")
            self.stats_day.configure(text=f"""
Day
Productive: {time.strftime("%H:%M:%S", time.gmtime(self.running_data["stats"]["day"]["productive"]))}
Unproductive: {time.strftime("%H:%M:%S", time.gmtime(self.running_data["stats"]["day"]["unproductive"]))}
Idle: {time.strftime("%H:%M:%S", time.gmtime(self.running_data["stats"]["day"]["idle"]))}""")
        self.root.after(1000, self.draw)
    
    def draw_infrequent(self):
        if self.window_visible:
            self.stats_month.configure(text=f"""
Month
Productive: {round(self.running_data["stats"]["month"]["productive"] // 3600)}
Unproductive: {round(self.running_data["stats"]["month"]["unproductive"] // 3600)}
Idle: {round(self.running_data["stats"]["month"]["idle"] // 3600)}""")
            self.stats_total.configure(text=f"""
Total
Productive: {round(self.running_data["stats"]["total"]["productive"] // 3600)}
Unproductive: {round(self.running_data["stats"]["total"]["unproductive"] // 3600)}
Idle: {round(self.running_data["stats"]["total"]["idle"] // 3600)}""")
        self.root.after(60000, self.draw_infrequent)
    
    def update(self):
        self.get_idle_duration()
        self.determine_state()
        self.root.after(1000, self.update)

    def start(self):
        print("Starting...")
        self.root.after(100, self.update)
        self.root.after(100, self.open_file)
        self.root.after(20000, self.auto_update_stats)
        self.root.after(1000, self.draw)
        self.root.after(1000, self.draw_infrequent)
        self.root.after(1500, self.check_date)
        self.root.mainloop()

if __name__ == "__main__":
    app = MonitorToolUI(minimize_on_start=False)
    app.start()