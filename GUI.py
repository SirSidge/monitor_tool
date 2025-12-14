import tkinter as tk
from tkinter import ttk
import psutil
from pystray import Icon, Menu, MenuItem
from PIL import Image
import time

class MonitorToolUI:
    def __init__(self, minimize_on_start=False):
        self.root = tk.Tk()
        self.root.geometry("800x580")
        self.root.title("Monitor Tool")
        self.prev_state = False

        style = ttk.Style()
        style.configure("Big.TLabel", font=("Helvetica", 24))

        self.label = ttk.Label(self.root, text="-- initialising --", style="Big.TLabel")
        self.label.pack(expand=True, pady=20)

        self.label2 = ttk.Label(self.root, text="-- initialising --", font=("Helvetica", 18), anchor="e")
        self.label2.pack(fill="x", padx=50, pady=10)

        if minimize_on_start:
            self.root.withdraw()

        image = Image.new('RGB', (64, 64), color = 'red')
        self.icon = Icon(
            'my_app',
            image,
            'My App',
            menu=Menu(
                MenuItem('Show', self.show_window),
                MenuItem('Quit', self.quit_app)
            )
        )
        self.icon.run_detached()

        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)

    def is_poe_running(self):
        return any(proc.name() == "PathOfExile.exe" for proc in psutil.process_iter(['name']))
    
    def show_window(self):
        self.root.deiconify()

    def hide_window(self):
        self.root.withdraw()

    def quit_app(self):
        self.icon.stop()
        self.root.quit()

    def refresh(self):
        cpu_usage = psutil.cpu_percent(interval=None)

        self.label.config(text=f"CPU Usage: {cpu_usage:.1f}%")

        date_suffix = time.strftime("%d%b").lstrip('0')
        file_path = fr'C:\monitoring tool - temp data\tmp_data_{date_suffix}.txt'

        if self.is_poe_running():
            if not self.prev_state:
                try:
                    with open(file_path, 'a', encoding='utf-8') as f:
                        f.write(f"start: {time.ctime()},")
                except FileNotFoundError:
                    print("The file does not exist.")
                self.prev_state = True
            self.label2.config(text=f"POE is running ✓", foreground="green")
        else:
            if self.prev_state:
                try:
                    with open(file_path, 'a', encoding='utf-8') as f:
                        f.write(f"end: {time.ctime()}\n")
                except FileNotFoundError:
                    print("The file does not exist.")
                self.prev_state = False
            self.label2.config(text=f"POE is not running ⚠", foreground="red")

        self.root.after(1000, self.refresh)

    def start(self):
        """Start the UI and refresh loop"""
        self.root.after(100, self.refresh)
        self.root.mainloop()


if __name__ == "__main__":
    app = MonitorToolUI(minimize_on_start=False)
    app.start()