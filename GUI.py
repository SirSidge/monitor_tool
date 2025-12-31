import tkinter as tk
from pystray import MenuItem, Icon, Menu
from PIL import Image
import threading

class MonitorToolUI:
    def __init__(self, minimize_on_start=True):
        self.root = tk.Tk()
        self.root.geometry("800x640")
        self.root.title("Monitor Tool")
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        self.window_visible = True
        self.icon = Icon("my_app")
        self.icon.icon = Image.new('RGB', (64, 64), color = 'black')
        self.icon.menu=Menu(
            MenuItem('Show', self.show_window),
            MenuItem('Quit', self.quit_app)
        )
        self.icon_thread = threading.Thread(target=self.icon.run, daemon=True)
        self.icon_thread.start()
    
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