import customtkinter as ctk
from pystray import MenuItem, Icon, Menu
from PIL import Image
import threading
import time
import psutil

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
        self._states = ["productive", "unproductive", "idle", "testing"]
        # Variables
        self.productivity_state = "testing"
        self.window_visible = True
        self.last_drawn = time.time()
        # Taskbar Icon
        self.icon = Icon("my_app")
        self.taskbar_icons = {
            "testing": Image.new('RGB', (64, 64), color = 'blue'),
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

    def set_status(self, state):
        print(state)
        if state not in self._states:
            raise ValueError(f"Invalid state: {state}")
        self.productivity_state = state
    
    def quit_app(self):
        self.icon.stop()
        self.root.destroy()

    def show_window(self):
        self.root.deiconify()
        self.window_visible = True

    def hide_window(self):
        self.root.withdraw()
        self.window_visible = False

    def update_taskbar_icon(self):
        self.icon.icon = self.taskbar_icons[self.productivity_state]

    """def get_processes_names(self, apps):
        return bool(apps & psutil.process_iter(['name']))"""
    
    def update_state(self):
        states = {
            "productive": {"Code.exe"},
            "unproductive": {"PathOfExile.exe", "Balls.exe"}
        }
        current_processes = {p.info['name'] for p in psutil.process_iter(['name']) if p.info['name']}
        for state in states:
            if bool(states[state] & current_processes):
                self.set_status(state)
                break
        else:
            self.set_status("testing")
    
    def draw(self):
        current_time = time.time()
        time_since_last_draw = current_time - self.last_drawn
        if time_since_last_draw >= 5:
            self.stats_label.configure(text=f"{self.productivity_state}")
    
    def update(self):
        self.update_taskbar_icon()
        self.update_state()
        if self.window_visible:
            #self.set_status("productive")
            self.draw()
        #else:
            #self.set_status("testing")
        self.root.after(1000, self.update)

    def start(self):
        print("Starting...")
        self.root.after(100, self.update)
        self.root.mainloop()

if __name__ == "__main__":
    app = MonitorToolUI(minimize_on_start=True)
    app.start()