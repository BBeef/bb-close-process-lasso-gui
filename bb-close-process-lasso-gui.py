import sys
import subprocess
from pathlib import Path
import time

import ctypes
import win32gui
import win32process
import psutil


if getattr(sys, "frozen", False):
    FILE = Path(sys.executable).resolve()
else:
    FILE = Path(__file__).resolve()


ROOT_DIR = FILE.parent


if getattr(sys, "frozen", False):
    TR = f'"{FILE}" --task'
else:
    TR = f'"{ROOT_DIR}\\.venv\\Scripts\\python.exe" "{FILE}" --task'


TASK_NAME = "BBCloseProcessLassoGUI"


def run_as_admin() -> None:
    """
    檢查是否為系統管理員權限
    """

    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()

    except Exception:
        is_admin = False

    if not is_admin:
        print()
        print("請以系統管理員執行")
        input("Press Enter...")

        sys.exit()


def hide_console() -> None:
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()

    if hwnd:
        ctypes.windll.user32.ShowWindow(hwnd, 0)


def check_desktop_ready() -> bool:
    """
    檢查是否登入且載入桌面
    """

    if not win32gui.FindWindow("Shell_TrayWnd", None):
        return False


    if not win32gui.FindWindow("Progman", None):
        return False


    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == 'explorer.exe':
                return True

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue


    return False


def create_task() -> None:
    """
    加入 Windows 工作排程器
    """

    cmd = [
        "schtasks",
        "/Create",
        "/TN", TASK_NAME,
        "/TR", TR,
        "/SC", "ONLOGON",
        "/RL", "HIGHEST",
        "/F"
    ]

    subprocess.run(
        cmd,
        check=True,
        creationflags=subprocess.CREATE_NO_WINDOW
    )

    cmd = [
        "powershell",
        "-Command",
        f"""
        $task = Get-ScheduledTask -TaskName '{TASK_NAME}'
        $task.Settings.DisallowStartIfOnBatteries = $false
        $task.Settings.StopIfGoingOnBatteries = $false
        Set-ScheduledTask -InputObject $task
        """.strip()
    ]

    subprocess.run(
        cmd,
        check=True,
        creationflags=subprocess.CREATE_NO_WINDOW
    )


def delete_task() -> None:
    """
    從 Windows 工作排程器中刪除
    """

    subprocess.run(
        [
            "schtasks",
            "/Delete",
            "/TN", TASK_NAME,
            "/F"
        ],
        creationflags=subprocess.CREATE_NO_WINDOW
    )


def kill_process_lasso_gui():

    target_pid = None

    def enum_windows_callback(hwnd, _):

        nonlocal target_pid


        if target_pid is not None:
            return True


        if not win32gui.IsWindowVisible(hwnd):
            return True


        title = win32gui.GetWindowText(hwnd)

        if "Process Lasso" in title:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            target_pid = pid

        return True


    win32gui.EnumWindows(enum_windows_callback, None)


    if target_pid is None:
        return


    try:
        process = psutil.Process(target_pid)
        process.kill()

    except (
        psutil.NoSuchProcess,
        psutil.AccessDenied,
        psutil.ZombieProcess
    ):
        pass


if __name__ == "__main__":

    if "--task" in sys.argv:

        hide_console()


        while not check_desktop_ready():
            time.sleep(1)


        for i in range(5):
            time.sleep(1)
            kill_process_lasso_gui()
            

        sys.exit(0)


    run_as_admin()


    print()
    print("這個軟體用來幫忙在開機時自動關閉彈出的 Process Lasso 視窗")
    print()
    print("請輸入 ( 1 / 2 / 3 ):")
    print("(1) 現在關閉 Process Lasso 視窗")
    print("(2) 開啟 開機自動執行")
    print("(3) 關閉 開機自動執行")

    n = input(" > ")

    if n == "1":
        kill_process_lasso_gui()

    elif n == "2":
        delete_task()

        time.sleep(1)

        create_task()

    elif n == "3":
        delete_task()

    else:
        print("輸入無效")


    print()
    print("結束")
    input("Press Enter...")
    sys.exit(0)