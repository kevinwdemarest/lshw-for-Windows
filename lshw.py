import ctypes
import ctypes.wintypes

class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]

# First, let's get CPU name from registry
def get_cpu_name():
    import winreg
    try: 
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                            r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
        cpu_name = winreg.QueryValueEx(key, "ProcessorNameString")[0]
        winreg.CloseKey(key)
        return cpu_name.strip()
    except:
        return "Unknown CPU"
        
# Get number of logical processors
def get_cpu_count():
    return ctypes.windll.kernel32.GetActiveProcessorCount(0xFFFF)

# Get CPU usage (this is a bit more complex)
class FILETIME(ctypes.Structure):
    _fields_ = [("dwLowDateTime", ctypes.c_ulong),
                ("dwHighDateTime", ctypes.c_ulong)]

def get_cpu_usage():
    idle_time = FILETIME()
    kernel_time = FILETIME()
    user_time = FILETIME()

    ctypes.windll.kernel32.GetSystemTimes(
        ctypes.byref(idle_time),
        ctypes.byref(kernel_time), 
        ctypes.byref(user_time)
     )

# Convert to 64-bit values
    idle = (idle_time.dwHighDateTime << 32) | idle_time.dwLowDateTime
    kernel = (kernel_time.dwHighDateTime << 32) | kernel_time.dwLowDateTime
    user = (user_time.dwHighDateTime << 32) | user_time.dwLowDateTime

# Calculate usage percentage (simplified)
    total = kernel + user
    if total > 0:
        usage = ((total - idle) / total) * 100
        return max(0, min(100, usage))
    return 0

def get_disk_space(drive="C:\\"):
    free_bytes = ctypes.c_ulonglong(0)
    total_bytes = ctypes.c_ulonglong(0)
    
    ctypes.windll.kernel32.GetDiskFreeSpaceExW(
        ctypes.c_wchar_p(drive),
        ctypes.pointer(free_bytes),
        ctypes.pointer(total_bytes),
        None
    )
    
    free_gb = free_bytes.value / (1024**3)
    total_gb = total_bytes.value / (1024**3)
    used_gb = total_gb - free_gb
    usage_percent = (used_gb / total_gb) * 100 if total_gb > 0 else 0
    
    return free_gb, total_gb, used_gb, usage_percent

print(f"CPU: {get_cpu_name()}")
print(f"CPU Cores: {get_cpu_count()}")
print(f"CPU Usage: {get_cpu_usage():.1f}%")

# Create the structure
memInfo = MEMORYSTATUSEX()
memInfo.dwLength = ctypes.sizeof(MEMORYSTATUSEX)

# Call the Windows API
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memInfo))

# Convert bytes to GB
total_ram_gb = memInfo.ullTotalPhys / (1024**3)
print(f"Total RAM: {total_ram_gb:.2f} GB")

# Available RAM
available_ram_gb = memInfo.ullAvailPhys / (1024**3)
print(f"Available RAM: {available_ram_gb:.2f} GB")

# Memory usage percentage
memory_usage = memInfo.dwMemoryLoad
print(f"Memory usage: {memory_usage}%")

print(f"Total RAM: {total_ram_gb:.2f} GB")

# Disk space
free, total, used, percent = get_disk_space()
print(f"Disk C: {used:.1f}GB used / {total:.1f}GB total ({percent:.1f}% full)")
print(f"Free space: {free:.1f}GB")
