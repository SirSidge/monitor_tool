import tkinter as tk
from tkinter import ttk
import psutil

root = tk.Tk()
root.geometry("800x580")
root.title("Monitor Tool")

# Optional: big font for label
style = ttk.Style()
style.configure("Big.TLabel", font=("Helvetica", 24))

label = ttk.Label(root, text="-- initialising --", style="Big.TLabel")
label.pack(expand=True, pady=20)

label2 = ttk.Label(root, text="-- initialising --", font=("Helvetica", 18), anchor="e")
label2.pack(fill="x", padx=50, pady=10)

def is_poe_running():
    """Fast check if PathOfExile.exe is running"""
    return any(proc.name() == "PathOfExile.exe" for proc in psutil.process_iter(['name']))

def refresh():
    # Update CPU usage (assuming get_cpu_usage() is fast; if not, replace with psutil.cpu_percent())
    try:
        from Monitoring import get_cpu_usage
        cpu_usage = get_cpu_usage()
    except:
        cpu_usage = psutil.cpu_percent(interval=None)  # non-blocking

    label.config(text=f"CPU Usage: {cpu_usage:.1f}%")

    # Update POE status efficiently
    if is_poe_running():
        label2.config(text="POE is running ✓", foreground="green")
    else:
        label2.config(text="POE is not running ⚠", foreground="red")

    # Schedule next update ONCE
    root.after(1000, refresh)

# Start the refresh loop
root.after(100, refresh)  # start almost immediately

# Make sure the window closes cleanly
root.protocol("WM_DELETE_WINDOW", root.destroy)

root.mainloop()