import customtkinter as ctk
from pystray import MenuItem, Icon, Menu
from PIL import Image
import threading

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
        self.window_visible = True
        self.icon = Icon("my_app")
        self.icon.icon = Image.new('RGB', (64, 64), color = 'black')
        self.icon.menu=Menu(
            MenuItem('Show', self.show_window),
            MenuItem('Quit', self.quit_app)
        )
        self.icon_thread = threading.Thread(target=self.icon.run, daemon=True)
        self.icon_thread.start()

        frame = ctk.CTkFrame(self.root, fg_color="gray20", corner_radius=10)
        frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        stats_label = ctk.CTkLabel(frame, text="Hello World!")
        stats_label.grid(row=0, column=0, padx=10, pady=10)

        processes_button = ctk.CTkButton(frame, text="Do not click me!", command=self.quit_app)
        processes_button.grid(row=1, column=0, padx=10, pady=10)
    
    def quit_app(self):
        self.icon.stop()
        self.root.destroy()

    def show_window(self):
        self.root.deiconify()
        self.window_visible = True

    def hide_window(self):
        self.root.withdraw()
        self.window_visible = False
    
    def update(self):
        # Runs every second
        self.root.after(1000, self.update)
        

    def start(self):
        self.root.mainloop()
        self.root.after(100, self.update)

if __name__ == "__main__":
    app = MonitorToolUI(minimize_on_start=True)
    app.start()