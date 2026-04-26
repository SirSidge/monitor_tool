import customtkinter as ctk
from pystray import MenuItem, Icon, Menu
from PIL import Image
import threading
import time
from datetime import date, timedelta
import psutil
import ctypes
from ctypes import wintypes, Structure, windll, c_uint, sizeof, byref
import json
from pathlib import Path
import os

class LASTINPUTINFO(Structure):
    _fields_ = [('cbSize', c_uint), ('dwTime', c_uint)]

class MonitorToolUI:
    def __init__(self, minimize_on_start=True):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.root = ctk.CTk()
        self.root.geometry("1280x700")
        self.root.title("Monitor Tool")
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)

        self.root.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        self.productivity_state = "idle"
        self.window_visible = True
        self.last_stat_update = time.time()
        self.inactive = False

        self.file_path = Path.home() / "AppData" / "Local" / "MonitorTool" / "running_data.json"

        self.running_data = {
            "metadata": {"last_active_date": date.today().isoformat()},
            "daily_stats": {},
            "total": {"productive": 0.0, "unproductive": 0.0, "idle": 0.0},
            "statuses": {
                "productive": {"Code.exe"},
                "unproductive": {"PathOfExile.exe", "Balls.exe"},
                "idle": set(),
            }
        }

        self.icon = Icon("MonitorTool")
        self.taskbar_icons = {
            "idle": Image.new('RGB', (64, 64), color='black'),
            "productive": Image.new('RGB', (64, 64), color='green'),
            "unproductive": Image.new('RGB', (64, 64), color='red'),
        }
        self.icon.icon = self.taskbar_icons[self.productivity_state]
        self.icon.menu = Menu(MenuItem('Show', self.show_window), MenuItem('Quit', self.quit_app))

        self.icon_thread = threading.Thread(target=self.icon.run, daemon=True)
        self.icon_thread.start()

        # Top frame
        self.frame = ctk.CTkFrame(self.root, fg_color="gray20", corner_radius=10)
        self.frame.grid(row=0, column=0, columnspan=5, padx=20, pady=10, sticky="ew")
        self.frame.grid_columnconfigure((1, 2, 3, 4), weight=1)

        # Fixed-width current status to prevent layout shift
        self.stats_label = ctk.CTkLabel(
            self.frame, 
            text="-- initialising --", 
            font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
            width=140,          # Fixed width in pixels
            anchor="w"
        )
        self.stats_label.grid(row=0, column=0, padx=15, pady=8, sticky="w")

        self.stats_day = ctk.CTkLabel(self.frame, text="-- initialising --", justify="left")
        self.stats_day.grid(row=0, column=1, padx=10, pady=8, sticky="ew")

        self.stats_yesterday = ctk.CTkLabel(self.frame, text="-- yesterday --", justify="left")
        self.stats_yesterday.grid(row=0, column=2, padx=10, pady=8, sticky="ew")

        self.stats_month = ctk.CTkLabel(self.frame, text="-- month --", justify="left")
        self.stats_month.grid(row=0, column=3, padx=10, pady=8, sticky="ew")

        self.stats_total = ctk.CTkLabel(self.frame, text="-- total --", justify="left")
        self.stats_total.grid(row=0, column=4, padx=10, pady=8, sticky="ew")

        self.quit_button = ctk.CTkButton(self.frame, text="Quit", width=80, command=self.quit_app)
        self.quit_button.grid(row=0, column=5, padx=10, pady=8, sticky="e")

        self.history_button = ctk.CTkButton(self.frame, text="View History", width=110, command=self.open_history_window)
        self.history_button.grid(row=0, column=6, padx=10, pady=8, sticky="e")

        # Process frames
        self.processes_list = ctk.CTkScrollableFrame(self.root, width=220, label_text="All Running Processes")
        self.processes_list.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.idle_processes = ctk.CTkScrollableFrame(self.root, width=220, label_text="Idle Processes")
        self.idle_processes.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        self.productive_processes = ctk.CTkScrollableFrame(self.root, width=220, label_text="Productive Processes")
        self.productive_processes.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

        self.unproductive_processes = ctk.CTkScrollableFrame(self.root, width=220, label_text="Unproductive Processes")
        self.unproductive_processes.grid(row=1, column=3, padx=10, pady=10, sticky="nsew")

        if minimize_on_start:
            self.root.after(1500, self.hide_window)

    def set_status(self, state):
        if state not in self.running_data["statuses"]:
            raise ValueError(f"Invalid state: {state}")

        current_time = time.time()
        today_str = date.today().isoformat()

        if today_str not in self.running_data["daily_stats"]:
            self.running_data["daily_stats"][today_str] = {"productive": 0.0, "unproductive": 0.0, "idle": 0.0}

        prev = self.productivity_state
        elapsed = current_time - self.last_stat_update

        self.running_data["daily_stats"][today_str][prev] += elapsed
        self.running_data["total"][prev] += elapsed

        self.last_stat_update = current_time
        self.productivity_state = state
        self.update_taskbar_icon()

    def calculate_month_stats(self):
        current_month = date.today().month
        current_year = date.today().year
        month_stats = {"productive": 0.0, "unproductive": 0.0, "idle": 0.0}

        for day_str, stats in self.running_data["daily_stats"].items():
            d = date.fromisoformat(day_str)
            if d.year == current_year and d.month == current_month:
                for k in month_stats:
                    month_stats[k] += stats.get(k, 0.0)
        return month_stats

    # ... (open_history_window, auto_update_stats, quit_app, show_window, hide_window, open_file, save_to_file, update_taskbar_icon remain the same as previous version)

    def open_history_window(self):
        win = ctk.CTkToplevel(self.root)
        win.title("Historical Stats")
        win.geometry("440x400")
        win.grab_set()

        ctk.CTkLabel(win, text="Enter date (YYYY-MM-DD):", font=ctk.CTkFont(size=13)).pack(pady=(20, 5))
        date_entry = ctk.CTkEntry(win, placeholder_text="2026-04-25", width=220)
        date_entry.pack(pady=5)

        result_label = ctk.CTkLabel(win, text="", justify="left", font=ctk.CTkFont(size=12))
        result_label.pack(pady=20, padx=30, fill="both")

        def show_day():
            d = date_entry.get().strip()
            stats = self.running_data.get("daily_stats", {}).get(d)
            if stats:
                txt = f"""Date: {d}

Productive:   {time.strftime("%H:%M:%S", time.gmtime(stats["productive"]))}
Unproductive: {time.strftime("%H:%M:%S", time.gmtime(stats["unproductive"]))}
Idle:         {time.strftime("%H:%M:%S", time.gmtime(stats["idle"]))}"""
                result_label.configure(text=txt)
            else:
                result_label.configure(text=f"No data recorded for {d}")

        ctk.CTkButton(win, text="Show Stats", command=show_day).pack(pady=10)

    def auto_update_stats(self):
        self.save_to_file()
        self.root.after(20000, self.auto_update_stats)

    def quit_app(self):
        self.save_to_file()
        try:
            self.icon.stop()
        except:
            pass
        self.root.destroy()

    def show_window(self):
        self.root.deiconify()
        self.window_visible = True
        self.draw()
        self.draw_infrequent()
        self.draw_yesterday()

    def hide_window(self):
        self.root.withdraw()
        self.window_visible = False

    def open_file(self):
        os.makedirs(self.file_path.parent, exist_ok=True)
        if not self.file_path.exists():
            self.save_to_file()
            return

        with open(self.file_path, "r", encoding='utf-8') as f:
            data = json.load(f)

        self.running_data = data
        if "daily_stats" not in self.running_data:
            self.running_data["daily_stats"] = {}
        if "total" not in self.running_data:
            self.running_data["total"] = {"productive": 0.0, "unproductive": 0.0, "idle": 0.0}

        if "statuses" in self.running_data:
            self.running_data["statuses"] = {k: set(v) for k, v in self.running_data["statuses"].items()}

    def save_to_file(self):
        os.makedirs(self.file_path.parent, exist_ok=True)
        data_to_save = self.running_data.copy()
        data_to_save["statuses"] = {k: list(v) for k, v in self.running_data["statuses"].items()}
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=4)

    def update_taskbar_icon(self):
        self.icon.icon = self.taskbar_icons[self.productivity_state]

    def get_foreground_process_name(self):
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if hwnd == 0: return None
        pid = wintypes.DWORD()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value == 0: return None
        try:
            return psutil.Process(pid.value).name()
        except:
            return None

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
        self.inactive = sec >= 300

    def check_date(self):
        today = date.today().isoformat()
        if self.running_data["metadata"]["last_active_date"] != today:
            self.running_data["metadata"]["last_active_date"] = today
        self.root.after(1500, self.check_date)

    def draw(self):
        if self.window_visible:
            self.stats_label.configure(text=f"Current: {self.productivity_state.upper()}")
            today_str = date.today().isoformat()
            today_stats = self.running_data["daily_stats"].get(today_str, {"productive": 0.0, "unproductive": 0.0, "idle": 0.0})

            self.stats_day.configure(text=f"""Today
Productive:   {time.strftime("%H:%M:%S", time.gmtime(today_stats["productive"]))}
Unproductive: {time.strftime("%H:%M:%S", time.gmtime(today_stats["unproductive"]))}
Idle:         {time.strftime("%H:%M:%S", time.gmtime(today_stats["idle"]))}""")
        self.root.after(1000, self.draw)

    def draw_yesterday(self):
        if self.window_visible:
            yesterday = (date.today() - timedelta(days=1)).isoformat()
            stats = self.running_data["daily_stats"].get(yesterday, {"productive": 0.0, "unproductive": 0.0, "idle": 0.0})
            self.stats_yesterday.configure(text=f"""Yesterday
Productive:   {time.strftime("%H:%M:%S", time.gmtime(stats["productive"]))}
Unproductive: {time.strftime("%H:%M:%S", time.gmtime(stats["unproductive"]))}
Idle:         {time.strftime("%H:%M:%S", time.gmtime(stats["idle"]))}""")
        self.root.after(30000, self.draw_yesterday)

    def draw_infrequent(self):
        if self.window_visible:
            month_stats = self.calculate_month_stats()
            self.stats_month.configure(text=f"""This Month
Productive:   {round(month_stats["productive"] // 3600)}h
Unproductive: {round(month_stats["unproductive"] // 3600)}h
Idle:         {round(month_stats["idle"] // 3600)}h""")

            self.stats_total.configure(text=f"""Total
Productive:   {round(self.running_data["total"]["productive"] // 3600)}h
Unproductive: {round(self.running_data["total"]["unproductive"] // 3600)}h
Idle:         {round(self.running_data["total"]["idle"] // 3600)}h""")
        self.root.after(60000, self.draw_infrequent)

    def update(self):
        self.get_idle_duration()
        self.determine_state()
        self.root.after(1000, self.update)

    # === Process management methods (unchanged from your last version) ===
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
                self.processes_list, text=name, anchor="w",
                command=lambda n=name: self.proc_button_event(n),
                fg_color="transparent", hover_color="#2A2A2A"
            )
            proc.grid(row=i, column=0, sticky="w", padx=10, pady=1)
        self.processes_list.update_idletasks()
        if hasattr(self.processes_list, '_parent_canvas'):
            self.processes_list._parent_canvas.yview_moveto(scroll_pos)
        self.root.after(10000, self.get_processes_list)

    def proc_button_event(self, proc_name):
        pop = ctk.CTkToplevel(self.root)
        self.current_popup = pop
        pop.title("Add App")
        pop.geometry("200x220")
        pop.grab_set()
        for i, (text, btn) in enumerate([("Idle", "idle"), ("Productive", "productive"), ("Unproductive", "unproductive")]):
            ctk.CTkButton(pop, text=text, command=lambda b=btn, n=proc_name: self.add_proc(b, n)).grid(row=i, column=0, padx=20, pady=4, sticky="ew")
        ctk.CTkButton(pop, text="Cancel", command=pop.destroy).grid(row=3, column=0, padx=20, pady=8, sticky="ew")

    def get_states_processes(self):
        for frame in (self.idle_processes, self.productive_processes, self.unproductive_processes):
            for w in frame.winfo_children(): w.destroy()

        for state, procs in self.running_data["statuses"].items():
            frame = getattr(self, f"{state}_processes")
            for i, proc in enumerate(sorted(procs)):
                btn = ctk.CTkButton(frame, text=proc, anchor="w",
                                    command=lambda s=state, n=proc: self.proc_state_btn_event(s, n),
                                    fg_color="transparent", hover_color="#2A2A2A")
                btn.grid(row=i, column=0, sticky="w", padx=10, pady=1)
        for frame in (self.idle_processes, self.productive_processes, self.unproductive_processes):
            frame.update_idletasks()
        self.root.after(10000, self.get_states_processes)

    def proc_state_btn_event(self, state, proc_name):
        pop = ctk.CTkToplevel(self.root)
        self.current_popup = pop
        pop.title("Remove App")
        pop.geometry("200x150")
        pop.grab_set()
        ctk.CTkButton(pop, text="Remove", command=lambda: self.remove_proc(state, proc_name)).grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        ctk.CTkButton(pop, text="Cancel", command=pop.destroy).grid(row=1, column=0, padx=20, pady=8, sticky="ew")

    def add_proc(self, btn, proc):
        if any(proc in s for s in self.running_data["statuses"].values()):
            print(f"{proc} already exists.")
        else:
            self.running_data["statuses"][btn].add(proc)
        if hasattr(self, 'current_popup'):
            self.current_popup.destroy()
        self.get_states_processes()

    def remove_proc(self, state, name):
        self.running_data["statuses"][state].discard(name)
        if hasattr(self, 'current_popup'):
            self.current_popup.destroy()
        self.get_states_processes()

    def start(self):
        print("Starting Monitor Tool...")
        self.root.after(100, self.update)
        self.root.after(100, self.open_file)
        self.root.after(20000, self.auto_update_stats)
        self.root.after(1000, self.draw)
        self.root.after(1000, self.draw_infrequent)
        self.root.after(1500, self.draw_yesterday)
        self.root.after(1500, self.check_date)
        self.root.after(1750, self.get_processes_list)
        self.root.after(1775, self.get_states_processes)
        self.root.mainloop()


if __name__ == "__main__":
    app = MonitorToolUI(minimize_on_start=False)
    app.start()