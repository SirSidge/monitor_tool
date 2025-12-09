import psutil

# Get CPU usage percentage
#cpu_percent = psutil.cpu_percent(interval=1)
#print(f"CPU Usage: {cpu_percent}")
_psutil_first = psutil.cpu_percent(interval=None)

def get_cpu_usage():
    return psutil.cpu_percent(interval=None)

def get_processes():
    processes = []
    for proc in psutil.process_iter():
        processes.append(proc.name())
    return processes