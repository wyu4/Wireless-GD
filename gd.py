import psutil
import win32api
import win32gui
import win32con
import win32process
import colors as col

class client:
    def __init__(self, name:str):
        self.name = name

    def get_pid(self) -> int|None:
        try:
            return next(process.pid for process in psutil.process_iter(['name', 'pid']) if process.info['name'] == self.name)
        except StopIteration:
            return None
    
    def get_first_window(self) -> int|None:
        pid = self.get_pid()
        if not pid:
            return None

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
    
    def get_window_name(self, hwnd:int|None) -> str:
        return win32gui.GetWindowText(hwnd) if hwnd is not None else win32gui.GetWindowText(self.get_first_window())
    
class GD(client):
    PROCESS_NAME = 'GeometryDash.exe'
    JUMP_KEYCODE = 0x57
    L_PARAMS = [0x00000001, 0xC0000001]

    def __init__(self):
        super().__init__(self.PROCESS_NAME)

    def jump(self, hwnd:int|None) -> None:
        if hwnd:
            win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, self.JUMP_KEYCODE, self.L_PARAMS[0])
            print(f'{col.OKCYAN}Jump sent to {super().get_window_name(hwnd)}{col.ENDC}')

    def release(self, hwnd:int|None) -> None:
        if hwnd:
            win32api.SendMessage(hwnd, win32con.WM_KEYUP, self.JUMP_KEYCODE, self.L_PARAMS[1])
            print(f'{col.OKCYAN}Release sent to {super().get_window_name(hwnd)}{col.ENDC}')