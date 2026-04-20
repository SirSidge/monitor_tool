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
        self.root.geometry("1200x640")
        self.root.title("Monitor Tool")
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        self.root.grid_columnconfigure((0,1,2,3), weight=1)
        self.root.grid_rowconfigure(1, weight=1)
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
            },
            "statuses": {
                "productive": {"Code.exe"},
                "unproductive": {"PathOfExile.exe", "Balls.exe"},
                "idle": set(),
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
        self.process_labels = []
        # Frame and widgets
        self.frame = ctk.CTkFrame(self.root, fg_color="gray20", corner_radius=10)
        self.frame.grid(row=0, column=0, columnspan=4, padx=20, pady=10, sticky="ew")
        self.frame.grid_columnconfigure((1, 2, 3), weight=1)
        self.stats_label = ctk.CTkLabel(self.frame, text="-- initialising --")
        self.stats_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        self.quit_button = ctk.CTkButton(self.frame, text="Quit", command=self.quit_app)
        self.quit_button.grid(row=1, column=0, padx=15, pady=10, sticky="w")
        self.stats_day = ctk.CTkLabel(self.frame, text="-- initialising --")
        self.stats_day.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.stats_month = ctk.CTkLabel(self.frame, text="-- initialising --")
        self.stats_month.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        self.stats_total = ctk.CTkLabel(self.frame, text="-- initialising --")
        self.stats_total.grid(row=0, column=3, padx=10, pady=10, sticky="ew")
        self.processes_list = ctk.CTkScrollableFrame(self.root, width=200, height=300, label_text="Running Processes")
        self.processes_list.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        """self.states_processes = ctk.CTkLabel(self.root, text="-- initialising --")
        self.states_processes.grid(row=1, column=1)"""
        self.idle_processes = ctk.CTkScrollableFrame(self.root, width=200, height=300, label_text="Idle Processes")
        self.idle_processes.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.productive_processes = ctk.CTkScrollableFrame(self.root, width=200, height=300, label_text="Productive Processes")
        self.productive_processes.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
        self.unproductive_processes = ctk.CTkScrollableFrame(self.root, width=200, height=300, label_text="Unproductive Processes")
        self.unproductive_processes.grid(row=1, column=3, padx=10, pady=10, sticky="nsew")
        # Minimize on Start (Note: Needs to stay at end of __init__ to avoid interrupting the building of the app.)
        if minimize_on_start:
            self.root.after(2000, self.hide_window)

    def set_status(self, state):
        print(state)
        if state in self.running_data["statuses"].keys():
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
        data_to_save = self.running_data.copy()
        data_to_save["statuses"] = {k: list(v) for k, v in self.running_data["statuses"].items()}
        
        obj_json = json.dumps(data_to_save, indent=4)   # ← Fixed
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
        if "statuses" in self.running_data:
            self.running_data["statuses"] = {
                k: set(v) for k, v in self.running_data["statuses"].items()
            }
        if "metadata" not in self.running_data:
            self.running_data["metadata"] = {"last_active_date": date.today().isoformat()}
        if "statuses" not in self.running_data:
            self.running_data["statuses"] = {
                "productive": {"Code.exe"},
                "unproductive": {"PathOfExile.exe", "Balls.exe"},
                "idle": set(),
            }

    def save_to_file(self):
        data_to_save = self.running_data.copy()
        data_to_save["statuses"] = {k: list(v) for k, v in self.running_data["statuses"].items()}
        
        obj_json = json.dumps(data_to_save, indent=4)   # ← Fixed
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
        
    def get_processes_list(self):
        if hasattr(self.processes_list, '_parent_canvas'):
            scroll_pos = self.processes_list._parent_canvas.yview()[0]
        else:
            scroll_pos = 0.0
        for widget in self.processes_list.winfo_children():
            widget.destroy()
        process_names = sorted({p.name() for p in psutil.process_iter(['name']) if p.name()})
        for i, name in enumerate(process_names):
            proc = ctk.CTkButton(
                self.processes_list,
                text=name,
                anchor="w",
                command=lambda name=name: self.proc_button_event(name),
                fg_color="transparent",
                hover_color="#2A2A2A",
            )
            proc.grid(row=i, column=0, sticky="w", padx=10, pady=1)
        self.processes_list.update_idletasks()
        self.processes_list._parent_canvas.yview_moveto(scroll_pos)
        self.root.after(10000, self.get_processes_list)

    def proc_button_event(self, proc_name):
        pop_up_window = ctk.CTkToplevel(self.root)
        self.current_popup = pop_up_window
        pop_up_window.title("Add App")
        pop_up_window.geometry("200x200")
        pop_up_window.grab_set()
        idle_btn = ctk.CTkButton(pop_up_window, text="Idle", command=lambda btn="idle", name=proc_name: self.add_proc(btn, name))
        prod_btn = ctk.CTkButton(pop_up_window, text="Productive", command=lambda btn="productive", name=proc_name: self.add_proc(btn, name))
        unprod_btn = ctk.CTkButton(pop_up_window, text="Unproductive", command=lambda btn="unproductive", name=proc_name: self.add_proc(btn, name))
        cancel_btn = ctk.CTkButton(pop_up_window, text="Cancel", command=pop_up_window.destroy)
        idle_btn.grid(row=0, column=0, padx=20, pady=4, sticky="ew")
        prod_btn.grid(row=1, column=0, padx=20, pady=4, sticky="ew")
        unprod_btn.grid(row=2, column=0, padx=20, pady=4, sticky="ew")
        cancel_btn.grid(row=3, column=0, padx=20, pady=8, sticky="ew")

    def get_states_processes(self):
        for widget in self.idle_processes.winfo_children():
            widget.destroy()
        for widget in self.productive_processes.winfo_children():
            widget.destroy()
        for widget in self.unproductive_processes.winfo_children():
            widget.destroy()
        for state, processes in self.running_data["statuses"].items():
            for i, process in enumerate(processes):
                if state == "idle":
                    proc_btn = ctk.CTkButton(
                        self.idle_processes,
                        text=process,
                        anchor="w",
                        command=lambda state=state, name=process: self.proc_state_btn_event(state, name),
                        fg_color="transparent",
                        hover_color="#2A2A2A",
                    )
                    proc_btn.grid(row=i, column=0, sticky="w", padx=10, pady=1)
                elif state == "productive":
                    proc_btn = ctk.CTkButton(
                        self.productive_processes,
                        text=process,
                        anchor="w",
                        command=lambda state=state, name=process: self.proc_state_btn_event(state, name),
                        fg_color="transparent",
                        hover_color="#2A2A2A",
                    )
                    proc_btn.grid(row=i, column=0, sticky="w", padx=10, pady=1)
                elif state == "unproductive":
                    proc_btn = ctk.CTkButton(
                        self.unproductive_processes,
                        text=process,
                        anchor="w",
                        command=lambda state=state, name=process: self.proc_state_btn_event(state, name),
                        fg_color="transparent",
                        hover_color="#2A2A2A",
                    )
                    proc_btn.grid(row=i, column=0, sticky="w", padx=10, pady=1)
        self.idle_processes.update_idletasks()
        self.productive_processes.update_idletasks()
        self.unproductive_processes.update_idletasks()
        self.root.after(10000, self.get_states_processes)
    
    def proc_state_btn_event(self, state, proc_name):
        pop_up_window = ctk.CTkToplevel(self.root)
        self.current_popup = pop_up_window
        pop_up_window.title("Remove App")
        pop_up_window.geometry("200x200")
        pop_up_window.grab_set()
        remove_btn = ctk.CTkButton(pop_up_window, text="Remove", command=lambda state=state, name=proc_name: self.remove_proc(state, name))
        cancel_btn = ctk.CTkButton(pop_up_window, text="Cancel", command=pop_up_window.destroy)
        remove_btn.grid(row=0, column=0, padx=20, pady=4, sticky="ew")
        cancel_btn.grid(row=1, column=0, padx=20, pady=8, sticky="ew")
    
    def remove_proc(self, state, name):
        if name in self.running_data["statuses"][state]:
            self.running_data["statuses"][state].discard(name)
            if hasattr(self, 'current_popup'):
                self.current_popup.destroy()
        else:
            print(f"{name} does not exist.")
            self.current_popup.destroy()
        self.get_states_processes()
    
    def add_proc(self, btn, proc):
        found = False
        for state in self.running_data["statuses"].values():
            if proc in state:
                found = True
                break
        if not found:
            self.running_data["statuses"][btn].add(proc)
            if hasattr(self, 'current_popup'):
                self.current_popup.destroy()
            self.draw_infrequent()
        else:
            print(f"{proc} already exists.")
            self.current_popup.destroy()
        self.get_states_processes()

    def determine_state(self):
        if not self.inactive:
            foreground_app = self.get_foreground_process_name()
            for k, v in self.running_data["statuses"].items():
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
        self.root.after(1750, self.get_processes_list)
        self.root.after(1775, self.get_states_processes)
        self.root.mainloop()

if __name__ == "__main__":
    app = MonitorToolUI(minimize_on_start=False)
    app.start()