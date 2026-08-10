import os
import subprocess
import winreg


def launch_app(name):
    path = find_app_path(name)
    try:
        if path:
            os.startfile(path)
            return "Launched."
        subprocess.Popen(["cmd", "/c", "start", "", name], shell=False)
        return "Launched."
    except Exception as error:
        return f"Failed to launch: {error}"


def run_command(command):
    try:
        subprocess.Popen(["cmd", "/c", "start", "", command], shell=False)
        return "Command executed."
    except Exception as error:
        return f"Failed: {error}"


def find_app_path(name):
    exe_name = name if name.lower().endswith(".exe") else f"{name}.exe"
    registry_root = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"
    for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        try:
            with winreg.OpenKey(root, rf"{registry_root}\{exe_name}") as key:
                return winreg.QueryValue(key, None)
        except OSError:
            continue
    return None
