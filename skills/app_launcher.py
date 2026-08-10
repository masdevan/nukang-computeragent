import os
import shutil
import subprocess
import sys


def launch_app(name):
    path = find_app_path(name)
    try:
        if path:
            if sys.platform == "win32":
                os.startfile(path)
            else:
                subprocess.Popen([path])
            return "Launched."
        if sys.platform == "win32":
            subprocess.Popen(["cmd", "/c", "start", "", name], shell=False)
        else:
            subprocess.Popen([name])
        return "Launched."
    except Exception as error:
        return f"Failed to launch: {error}"


def run_command(command):
    try:
        if sys.platform == "win32":
            subprocess.Popen(["cmd", "/c", "start", "", command], shell=False)
        else:
            subprocess.Popen(command, shell=True)
        return "Command executed."
    except Exception as error:
        return f"Failed: {error}"


def find_app_path(name):
    found = shutil.which(name)
    if found:
        return found
    if sys.platform != "win32":
        return None
    import winreg

    exe_name = name if name.lower().endswith(".exe") else f"{name}.exe"
    registry_root = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"
    for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        try:
            with winreg.OpenKey(root, rf"{registry_root}\{exe_name}") as key:
                return winreg.QueryValue(key, None)
        except OSError:
            continue
    return None
