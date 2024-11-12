import psutil
import win32api
import win32gui
import win32con
import win32process
from pywintypes import error as winErr
import ctypes

PROCESS_NAME = 'GeometryDash.exe'
JUMP_KEY = 0x57

def get_pid(name:str|None=PROCESS_NAME):
    try:
        return next(process.pid for process in psutil.process_iter(['name', 'pid']) if process.info['name'] == name)
    except StopIteration:
        return None

def get_window(pid:int):
    global result
    result = None
    def callback(handle, pid):
        global result
        if win32gui.IsWindowVisible(handle) and win32gui.IsWindowEnabled(handle):
            _, window_pid = win32process.GetWindowThreadProcessId(handle)
            if window_pid == pid:
                result = handle
                return handle
    win32gui.EnumWindows(callback, pid)
    return result

def jump(pid:int):
    try:
        handle = get_window(pid)
        if handle:
            # win32gui.ShowWindow(handle, win32con.SW_RESTORE)
            # win32gui.SetForegroundWindow(handle)
            win32api.SendMessage(handle, win32con.WM_KEYDOWN, JUMP_KEY, 0x00000001)
            # win32api.keybd_event(JUMP_KEY, 0, 0, 0)

            print(f'Jump sent to {win32gui.GetWindowText(handle)}')
    except winErr:
        return

def release(pid:int):
    try:
        handle = get_window(pid)
        if handle:
            # win32gui.ShowWindow(handle, win32con.SW_RESTORE)
            # win32gui.SetForegroundWindow(handle)
            # win32api.SendMessage(JUMP_KEY, 0, 2 ,0)
            win32api.SendMessage(handle, win32con.WM_KEYUP, JUMP_KEY, 0xC0000001)
            # win32api.keybd_event(JUMP_KEY, 0, 2, 0)

            print(f'Release sent to {win32gui.GetWindowText(handle)}')
    except winErr:
        return