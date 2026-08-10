import ctypes
import platform
import sys
from ctypes import wintypes


def collect_device_info():
    return {
        "os": os_name(),
        "screen": screen_info(),
        "cpu": cpu_name(),
        "ram_gb": ram_gb(),
    }


def os_name():
    if sys.platform != "win32":
        return platform.platform()
    try:
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
        ) as key:
            product = winreg.QueryValueEx(key, "ProductName")[0]
            display = winreg.QueryValueEx(key, "DisplayVersion")[0]
            build = winreg.QueryValueEx(key, "CurrentBuildNumber")[0]
        return f"{product} {display} (build {build})"
    except OSError:
        return platform.platform()


def screen_info():
    from PySide6.QtWidgets import QApplication

    screens = QApplication.screens()
    if not screens:
        return "unknown"
    primary = QApplication.primaryScreen()
    lines = []
    for index, screen in enumerate(screens):
        size = screen.size()
        scale = round(screen.devicePixelRatio() * 100)
        name = f"Screen {index + 1}"
        if screen == primary:
            name += " (primary)"
        line = f"{name}: {size.width()}x{size.height()} @ {scale}%"
        ratio = size.width() / size.height()
        if ratio >= 3.0:
            line += " (super ultrawide)"
        elif ratio >= 2.2:
            line += " (ultrawide)"
        lines.append(line)
    return "\n".join(lines)


def cpu_name():
    if sys.platform != "win32":
        return platform.processor()
    try:
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0"
        ) as key:
            return winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
    except OSError:
        return platform.processor()


def ram_gb():
    class MemoryStatusEx(ctypes.Structure):
        _fields_ = [
            ("length", wintypes.DWORD),
            ("memory_load", wintypes.DWORD),
            ("total_phys", ctypes.c_uint64),
            ("avail_phys", ctypes.c_uint64),
            ("total_page", ctypes.c_uint64),
            ("avail_page", ctypes.c_uint64),
            ("total_virtual", ctypes.c_uint64),
            ("avail_virtual", ctypes.c_uint64),
            ("avail_extended_virtual", ctypes.c_uint64),
        ]

    status = MemoryStatusEx()
    status.length = ctypes.sizeof(MemoryStatusEx)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
    return round(status.total_phys / (1024**3))


def format_device_info(info):
    return (
        f"OS: {info['os']}\n"
        f"Screen: {info['screen']}\n"
        f"CPU: {info['cpu']}\n"
        f"RAM: {info['ram_gb']} GB"
    )
