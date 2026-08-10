import os
import shutil
import subprocess
import sys


def launch_app(name):
    path = find_app_path(name)
    if path is None:
        return f"Application not found: {name}"
    try:
        if sys.platform == "win32":
            os.startfile(path)
        else:
            subprocess.Popen([path])
        return "Launched."
    except Exception as error:
        return f"Failed to launch: {error}"


def run_command(command):
    token = resolve_command_token(command)
    if token is None:
        return f"Command not found: {command}"
    try:
        if sys.platform == "win32":
            subprocess.Popen(["cmd", "/c", "start", "", command], shell=False)
        else:
            subprocess.Popen(command, shell=True)
        return "Command executed."
    except Exception as error:
        return f"Failed: {error}"


def resolve_command_token(command):
    token = command.strip().split()[0].strip('"') if command.strip() else ""
    if token and find_app_path(token):
        return token
    return None


def find_app_path(name):
    exe_name = name if name.lower().endswith(".exe") else f"{name}.exe"
    found = shutil.which(exe_name)
    if found:
        return found
    if sys.platform == "win32":
        import winreg

        registry_root = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"
        for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            try:
                with winreg.OpenKey(root, rf"{registry_root}\{exe_name}") as key:
                    return winreg.QueryValue(key, None)
            except OSError:
                continue
    found = shutil.which(name)
    if found and found.lower().endswith(".exe"):
        return found
    return None
