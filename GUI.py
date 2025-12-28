import tkinter as tk
from tkinter import ttk
import psutil
from pystray import Icon, Menu, MenuItem
from PIL import Image
import time
import json
import ctypes
from ctypes import wintypes, Structure, windll, c_uint, c_ulonglong, sizeof, byref
import os
from pathlib import Path

class LASTINPUTINFO(Structure):
    _fields_ = [
        ('cbSize', c_uint),
        ('dwTime', c_uint),
    ]

class MonitorToolUI:
    _VALID_STATES = {"productive", "idle", "unproductive"}

    def __init__(self, minimize_on_start=False):
        self.root = tk.Tk()
        self.root.protocol("WM_SAVE_YOURSELF", self.log_shutdown)
        self.root.geometry("800x640") #Window size
        self.root.title("Monitor Tool")
        self.prev_state = False
        self.root.withdraw()
        self.taskbar_image = Image.new('RGB', (64, 64), color = 'green')
        self.start_time = time.time()
        self.alarm = False
        self.productivity_status = "idle"
        self.updating_processes = False
        self._last_process_update = time.time()
        self.temp_stats = {}
        self._idle_time = False

        style = ttk.Style()
        style.configure("Big.TLabel", font=("Helvetica", 24))

        self.cpu_label = ttk.Label(self.root, text="-- initialising --", style="Big.TLabel")
        self.cpu_label.pack(expand=True, pady=20)

        # Foreground app display text
        self.foreground_label = ttk.Label(self.root, text="-- initialising --", font=("Helvetica", 18), anchor="ne")
        self.foreground_label.pack(fill="x", padx=50, pady=10)

        self.poe_label = ttk.Label(self.root, text="-- initialising --", font=("Helvetica", 18), anchor="e")
        self.poe_label.pack(fill="x", padx=50, pady=10)

        self.timer_label = ttk.Label(self.root, text="", font=("Helvetica", 14), foreground="red", anchor="e")
        self.timer_label.pack(fill="x", padx=50, pady=(0, 20))

        # Stats
        self.stats_label = ttk.Label(self.root, text="Productive\nDay:\nWeek:\nMonth:\nTotal:\nUnproductive\nDay:\nWeek:\nMonth:\nTotal:\nIdle\nDay:\nWeek:\nMonth:\nTotal:", font=("Helvetica", 14), anchor="nw")
        self.stats_label.pack(fill="x", padx=50, pady=(0, 20))

        # Scrollable list-box for currently running process names
        header = ttk.Label(self.root, text="Running process names (for debugging):", font=("Helvetica", 12))
        header.pack(anchor="w", padx=50, pady=(0, 5))
        list_frame = ttk.Frame(self.root)
        list_frame.pack(fill="both", expand=True, padx=50, pady=20)
        self.process_listbox = tk.Listbox(list_frame, font=("Consolas", 10), activestyle="none")
        self.process_listbox.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.process_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.process_listbox.config(yscrollcommand=scrollbar.set)
        self.process_button = ttk.Button(self.root, text="Display processes", command=self.toggle_process_updates)
        self.process_button.pack(pady=10)

        self.log_startup()

        if minimize_on_start:
            self.root.withdraw()

        self.icon = Icon(
            'my_app',
            self.taskbar_image,
            'My App',
            menu=Menu(
                MenuItem('Show', self.show_window),
                MenuItem('Quit', self.quit_app)
            )
        )
        self.icon.run_detached()

        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)

    def log_startup(self):
        stats_path = Path(r'C:\monitoring tool - temp data\stats.json')
        
        try:
            with open(stats_path, "r", encoding='utf-8') as f:
                self.temp_stats = json.load(f)
            print("Successfully loaded stats.json")  # Debug
        except FileNotFoundError:
            print("File not found - creating new one")  # Debug
            self._create_default_stats(stats_path)
        except json.JSONDecodeError as e:
            print(f"Corrupted JSON: {e} - recreating file")  # Debug
            self._create_default_stats(stats_path)
        except Exception as e:
            print(f"Unexpected error reading file: {e} - recreating")  # Debug
            self._create_default_stats(stats_path)
        with open(self.get_file_path(), 'a', encoding='utf-8') as f:
            f.write(f"Monitoring started: {time.ctime()}\n")

    def _create_default_stats(self, stats_path: Path):
        temp_data = {
            "productive": {"day": 0, "week": 0, "month": 0, "total": 0},
            "unproductive": {"day": 0, "week": 0, "month": 0, "total": 0},
            "idle": {"day": 0, "week": 0, "month": 0, "total": 0}
        }
        
        try:
            # Ensure the directory exists
            stats_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write with explicit encoding
            with open(stats_path, 'w', encoding='utf-8') as f:
                json.dump(temp_data, f, indent=4)
            
            print("Successfully created new stats.json")  # Debug
            self.temp_stats = temp_data
        except Exception as e:
            print(f"FAILED to write stats.json: {e}")
            # As a fallback, use defaults in memory (app can still run)
            self.temp_stats = temp_data
    
    def log_shutdown(self):
        self._set_status("idle")
        with open(fr'C:\monitoring tool - temp data\stats.json', "w", encoding='utf-8') as f:
            self.update_stats()
            json.dump(self.temp_stats, f, indent=4)
        with open(self.get_file_path(), 'a', encoding='utf-8') as f:
            if self.prev_state:
                f.write(f"end: {time.ctime()}\n")
            f.write(f"Monitoring ended: {time.ctime()}\n")

    def _set_status(self, state):
        if state not in self._VALID_STATES:
            raise ValueError(f"Invalid state: {state}")
        self.productivity_status = state

    def get_idle_duration(self):
        lastInputInfo = LASTINPUTINFO()
        lastInputInfo.cbSize = sizeof(lastInputInfo)
        windll.user32.GetLastInputInfo(byref(lastInputInfo))
        millis = windll.kernel32.GetTickCount64() - lastInputInfo.dwTime
        if (millis / 1000.0) >= 300:
            self._idle_time = True
        else:
            self._idle_time = False

    # Get foreground app
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

    def update_process_list(self):
        self.process_listbox.delete(0, tk.END)
        process_names = sorted({p.name() for p in psutil.process_iter(['name']) if p.name()})
        for name in process_names:
            self.process_listbox.insert(tk.END, name)

    def toggle_process_updates(self):
        if not self.updating_processes:
            self.updating_processes = True
            self.process_button.config(text="Stop")
            self.update_process_list()
            self.continue_process_updates()
        else:
            self.updating_processes = False
            self.process_button.config(text="Display processes")

    def continue_process_updates(self):
        if not self.updating_processes:
            return
        current_time = time.time()
        if current_time - self._last_process_update >= 5:
            self.update_process_list()
            self._last_process_update = current_time
        self.root.after(1000, self.continue_process_updates)

    def update_stats(self):
        current_time = time.time()
        time_dif_temp = current_time - self._last_process_update
        if time_dif_temp >= 10:
            self.get_idle_duration()
            if self.productivity_status == "productive":
                self.temp_stats["productive"]["day"] += (time_dif_temp/3600)
                self.temp_stats["productive"]["week"] += (time_dif_temp/3600)
                self.temp_stats["productive"]["month"] += (time_dif_temp/3600)
                self.temp_stats["productive"]["total"] += (time_dif_temp/3600)
            elif self.productivity_status == "unproductive":
                self.temp_stats["unproductive"]["day"] += (time_dif_temp/3600)
                self.temp_stats["unproductive"]["week"] += (time_dif_temp/3600)
                self.temp_stats["unproductive"]["month"] += (time_dif_temp/3600)
                self.temp_stats["unproductive"]["total"] += (time_dif_temp/3600)
            elif self.productivity_status == "idle":
                self.temp_stats["idle"]["day"] += (time_dif_temp/3600)
                self.temp_stats["idle"]["week"] += (time_dif_temp/3600)
                self.temp_stats["idle"]["month"] += (time_dif_temp/3600)
                self.temp_stats["idle"]["total"] += (time_dif_temp/3600)
            self.stats_label.config(text=f"Productive\nDay: {round(self.temp_stats["productive"]["day"], 10)}h\nWeek: {round(self.temp_stats["productive"]["week"])}h\nMonth: {round(self.temp_stats["productive"]["month"])}h\nTotal: {round(self.temp_stats["productive"]["total"])}h\n\nUnproductive\nDay: {round(self.temp_stats["unproductive"]["day"], 10)}h\nWeek: {round(self.temp_stats["unproductive"]["week"])}h\nMonth: {round(self.temp_stats["unproductive"]["month"])}h\nTotal: {round(self.temp_stats["unproductive"]["total"])}h\n\nIdle\nDay: {round(self.temp_stats["idle"]["day"], 10)}h\nWeek: {round(self.temp_stats["idle"]["week"])}h\nMonth: {round(self.temp_stats["idle"]["month"])}h\nTotal: {round(self.temp_stats["idle"]["total"])}h")
            self._last_process_update = current_time
        self.root.after(1000, self.update_stats)

    def is_game_running(self):
        unproductive_apps = ["PathOfExile.exe", "Balls.exe"]
        return any(proc.name() in unproductive_apps for proc in psutil.process_iter(['name']))
    
    def is_vscode_running(self):
        return any(proc.name() == "Code.exe" for proc in psutil.process_iter(['name']))
    
    def show_window(self):
        self.root.deiconify()

    def hide_window(self):
        self.root.withdraw()

    def quit_app(self):
        self.log_shutdown()
        self.icon.stop()
        self.root.quit()

    def get_file_path(self):
        date_suffix = time.strftime("%d%b").lstrip('0')
        return fr'C:\monitoring tool - temp data\tmp_data_{date_suffix}.txt'

    def refresh(self):
        cpu_usage = psutil.cpu_percent(interval=None)
        self.foreground_label.config(text=f"Foreground App: TBC")
        self.cpu_label.config(text=f"CPU Usage: {cpu_usage:.1f}%")
        self.update_stats()

        if not self._idle_time and self.is_game_running():
            self._set_status("unproductive")
            if not self.prev_state:
                try:
                    with open(self.get_file_path(), 'a', encoding='utf-8') as f:
                        f.write(f"start: {time.ctime()},")
                except FileNotFoundError:
                    print("The file does not exist.")
                self.prev_state = True
                self.start_time = time.time()
                self.alarm = False
                self.timer_label.config(text="")
            self.poe_label.config(text=f"Unproductive ⚠: {self.get_foreground_process_name()}", foreground="red")
            new_image = Image.new('RGB', (64, 64), 'red')
            self.icon.icon = new_image
            elapsed_time = time.time() - self.start_time
            if elapsed_time >= 7200 and not self.alarm: #7200 seconds
                self.timer_label.config(text="2 hours depleted")
                self.alarm = True
        elif not self._idle_time and self.is_vscode_running():
            if self.prev_state:
                try:
                    with open(self.get_file_path(), 'a', encoding='utf-8') as f:
                        f.write(f"end: {time.ctime()}\n")
                except FileNotFoundError:
                    print("The file does not exist.")
                self.prev_state = False
            new_image = Image.new('RGB', (64, 64), 'green')
            self.icon.icon = new_image
            self._set_status("productive")
            self.poe_label.config(text=f"Productive ✓: {self.get_foreground_process_name()}", foreground="green")
        else:
            self._set_status("idle")
            if self.prev_state:
                try:
                    with open(self.get_file_path(), 'a', encoding='utf-8') as f:
                        f.write(f"end: {time.ctime()}\n")
                except FileNotFoundError:
                    print("The file does not exist.")
                self.prev_state = False
            self.poe_label.config(text=f"Idle: {self.get_foreground_process_name()}", foreground="black")
            new_image = Image.new('RGB', (64, 64), 'black')
            self.icon.icon = new_image

        self.root.after(1000, self.refresh)

    def start(self):
        self.root.after(100, self.refresh)
        self.root.mainloop()


if __name__ == "__main__":
    app = MonitorToolUI(minimize_on_start=False)
    app.start()