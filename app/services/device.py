import ctypes
import platform
import sys
from ctypes import wintypes


def collect_device_info():
    info = {
        "os": os_name(),
        "screen": screen_info(),
        "cpu": cpu_name(),
        "ram_gb": ram_gb(),
    }
    active = active_screen_info()
    if active is not None:
        info["screen"] += (
            f"\nActive screen: {active['width']}x{active['height']} "
            f"at ({active['x']},{active['y']})"
        )
    return info


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


class MonitorInfo(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", wintypes.RECT),
        ("rcWork", wintypes.RECT),
        ("dwFlags", wintypes.DWORD),
    ]


class Guid(ctypes.Structure):
    _fields_ = [
        ("data1", wintypes.DWORD),
        ("data2", wintypes.WORD),
        ("data3", wintypes.WORD),
        ("data4", ctypes.c_ubyte * 8),
    ]


MONITOR_DEFAULTTONEAREST = 2
CLSID_VIRTUAL_DESKTOP_MANAGER = (0xAA509086, 0x5CA9, 0x4C25, (0x8F, 0x95, 0x58, 0x9D, 0x3C, 0x07, 0xB4, 0x8A))
IID_IVIRTUAL_DESKTOP_MANAGER = (0xA5CD92FF, 0x29BE, 0x454C, (0x8D, 0x04, 0xD8, 0x28, 0x79, 0xFB, 0x3F, 0x1B))


def active_screen_info():
    if sys.platform != "win32":
        return None
    user32 = ctypes.windll.user32
    foreground = user32.GetForegroundWindow()
    if foreground:
        monitor = user32.MonitorFromWindow(foreground, MONITOR_DEFAULTTONEAREST)
    else:
        point = wintypes.POINT()
        user32.GetCursorPos(ctypes.byref(point))
        monitor = user32.MonitorFromPoint(point, MONITOR_DEFAULTTONEAREST)
    if not monitor:
        return None
    info = MonitorInfo()
    info.cbSize = ctypes.sizeof(MonitorInfo)
    if not user32.GetMonitorInfoW(monitor, ctypes.byref(info)):
        return None
    rect = info.rcMonitor
    return {
        "x": rect.left,
        "y": rect.top,
        "width": rect.right - rect.left,
        "height": rect.bottom - rect.top,
    }


def desktop_manager():
    ole32 = ctypes.windll.ole32
    ole32.CoInitializeEx(None, 0)
    clsid = Guid(*CLSID_VIRTUAL_DESKTOP_MANAGER)
    iid = Guid(*IID_IVIRTUAL_DESKTOP_MANAGER)
    ptr = ctypes.c_void_p()
    hr = ole32.CoCreateInstance(
        ctypes.byref(clsid), None, 1, ctypes.byref(iid), ctypes.byref(ptr)
    )
    if hr != 0:
        return None
    return ptr


def current_desktop_guid():
    manager = desktop_manager()
    if manager is None:
        return None
    try:
        from skills.general.screenshot import ScreenshotCapture

        user32 = ctypes.windll.user32
        foreground = user32.GetForegroundWindow()
        if not foreground:
            point = wintypes.POINT()
            user32.GetCursorPos(ctypes.byref(point))
            foreground = user32.WindowFromPoint(point)
        if not foreground:
            return None
        return manager_get_window_desktop_id(manager, foreground)
    finally:
        release_manager(manager)


def virtual_desktops():
    manager = desktop_manager()
    if manager is None:
        return None
    try:
        from skills.general.screenshot import ScreenshotCapture

        desktops = {}
        for title in ScreenshotCapture().list_windows():
            user32 = ctypes.windll.user32
            hwnd = user32.FindWindowW(None, title)
            if not hwnd:
                continue
            desktop_id = manager_get_window_desktop_id(manager, hwnd)
            if desktop_id is None:
                continue
            desktops.setdefault(desktop_id, []).append(title)
        current = current_desktop_guid()
        return desktops, current
    finally:
        release_manager(manager)


def manager_get_window_desktop_id(manager, hwnd):
    fn = get_manager_method(manager, 4)
    guid = Guid()
    if fn(manager, hwnd, ctypes.byref(guid)) != 0:
        return None
    return guid_string(guid)


def manager_move_window_to_desktop(manager, hwnd, desktop_id):
    fn = get_manager_method(manager, 5)
    guid = parse_guid(desktop_id)
    if guid is None:
        return False
    return fn(manager, hwnd, ctypes.byref(guid)) == 0


def get_manager_method(manager, index):
    vtable = ctypes.cast(
        manager, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))
    ).contents
    return ctypes.cast(
        vtable[index],
        ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p),
    )


def guid_string(guid):
    data4 = bytes(guid.data4)
    return (
        f"{guid.data1:08x}-{guid.data2:04x}-{guid.data3:04x}-"
        f"{data4[0]:02x}{data4[1]:02x}-{data4[2]:02x}{data4[3]:02x}{data4[4]:02x}{data4[5]:02x}{data4[6]:02x}{data4[7]:02x}"
    )


def parse_guid(text):
    parts = text.strip("{}").split("-")
    if len(parts) != 5:
        return None
    try:
        guid = Guid()
        guid.data1 = int(parts[0], 16)
        guid.data2 = int(parts[1], 16)
        guid.data3 = int(parts[2], 16)
        tail = parts[3] + parts[4]
        guid.data4 = (ctypes.c_ubyte * 8)(*bytes.fromhex(tail))
        return guid
    except ValueError:
        return None


def release_manager(manager):
    vtable = ctypes.cast(
        manager, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))
    ).contents
    release = ctypes.cast(vtable[2], ctypes.WINFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p))
    release(manager)


def format_device_info(info):
    return (
        f"OS: {info['os']}\n"
        f"Screen: {info['screen']}\n"
        f"CPU: {info['cpu']}\n"
        f"RAM: {info['ram_gb']} GB"
    )
