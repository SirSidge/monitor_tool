import tkinter as tk
from tkinter import ttk
import psutil
from pystray import Icon, Menu, MenuItem
from PIL import Image
import time

class MonitorToolUI:
    def __init__(self, minimize_on_start=False):
        self.root = tk.Tk()
        self.root.protocol("WM_SAVE_YOURSELF", self.log_shutdown)
        self.root.geometry("800x580")
        self.root.title("Monitor Tool")
        self.prev_state = False
        self.root.withdraw()
        self.taskbar_image = Image.new('RGB', (64, 64), color = 'green')
        self.start_time = time.time()
        self.alarm = False

        style = ttk.Style()
        style.configure("Big.TLabel", font=("Helvetica", 24))

        self.label = ttk.Label(self.root, text="-- initialising --", style="Big.TLabel")
        self.label.pack(expand=True, pady=20)

        self.label2 = ttk.Label(self.root, text="-- initialising --", font=("Helvetica", 18), anchor="e")
        self.label2.pack(fill="x", padx=50, pady=10)

        self.timer_label = ttk.Label(self.root, text="", font=("Helvetica", 14), foreground="red", anchor="e")
        self.timer_label.pack(fill="x", padx=50, pady=(0, 20))

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
        with open(self.get_file_path(), 'a', encoding='utf-8') as f:
            f.write(f"Monitoring started: {time.ctime()}\n")
    
    def log_shutdown(self):
        with open(self.get_file_path(), 'a', encoding='utf-8') as f:
            if self.prev_state:
                f.write(f"end: {time.ctime()}\n")
            f.write(f"Monitoring ended: {time.ctime()}\n")

    def is_poe_running(self):
        return any(proc.name() == "PathOfExile.exe" for proc in psutil.process_iter(['name']))
    
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

        self.label.config(text=f"CPU Usage: {cpu_usage:.1f}%")

        if self.is_poe_running():
            if not self.prev_state:
                try:
                    with open(self.get_file_path(), 'a', encoding='utf-8') as f:
                        f.write(f"start: {time.ctime()},")
                except FileNotFoundError:
                    print("The file does not exist.")
                self.prev_state = True
                self.start_time = time.time()
            self.label2.config(text=f"POE is running ⚠", foreground="red")
            new_image = Image.new('RGB', (64, 64), 'red')
            self.icon.icon = new_image
        else:
            if self.prev_state:
                try:
                    with open(self.get_file_path(), 'a', encoding='utf-8') as f:
                        f.write(f"end: {time.ctime()}\n")
                except FileNotFoundError:
                    print("The file does not exist.")
                self.prev_state = False
            self.label2.config(text=f"POE is not running ✓", foreground="green")
            new_image = Image.new('RGB', (64, 64), 'green')
            self.icon.icon = new_image

        elapsed_time = time.time() - self.start_time
        if elapsed_time >= 7200 and not self.alarm:
            self.timer_label.config(text="2 hours depleted")
            self.alarm = True
        else:
            if not self.is_poe_running():
                self.timer_label.config(text="")
                self.alarm = False

        self.root.after(1000, self.refresh)

    def start(self):
        self.root.after(100, self.refresh)
        self.root.mainloop()


if __name__ == "__main__":
    app = MonitorToolUI(minimize_on_start=False)
    app.start()