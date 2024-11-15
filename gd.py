import psutil
import win32api
import win32gui
import win32con
import win32process
import colors as col

class client:
    L_PARAMS = [0x00000001, 0xC0000001]

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
    
    def keydown(self, hwnd:int|None, keycode:int|None=0x00) -> bool:
        if hwnd:
            win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, keycode, self.L_PARAMS[0])
            return True
        return False

    def keyup(self, hwnd:int|None, keycode:int|None=0x00) -> bool:
        if hwnd:
            win32api.SendMessage(hwnd, win32con.WM_KEYUP, keycode, self.L_PARAMS[1])
            return True
        return False
    
class GD(client):
    PROCESS_NAME = 'GeometryDash.exe'
    LEFT_KEYCODE = 0x41
    RIGHT_KEYCODE = 0x44
    JUMP_KEYCODE = 0x57

    def __init__(self):
        super().__init__(self.PROCESS_NAME)

    def jump(self, hwnd:int|None) -> None:
        if super().keydown(hwnd, self.JUMP_KEYCODE):
            print(f'{col.OKCYAN}Jump sent to {hwnd}{col.ENDC}')

    def jump_release(self, hwnd:int|None) -> None:
        if super().keyup(hwnd, self.JUMP_KEYCODE):
            print(f'{col.OKCYAN}Jump release sent to {hwnd}{col.ENDC}')

    def left(self, hwnd:int|None) -> None:
        if super().keydown(hwnd, self.LEFT_KEYCODE):
            print(f'{col.OKCYAN}Left sent to {hwnd}{col.ENDC}')

    def left_release(self, hwnd:int|None) -> None:
        if super().keyup(hwnd, self.LEFT_KEYCODE):
            print(f'{col.OKCYAN}Left release sent to {hwnd}{col.ENDC}')

    def right(self, hwnd:int|None) -> None:
        if super().keydown(hwnd, self.RIGHT_KEYCODE):
            print(f'{col.OKCYAN}Right sent to {hwnd}{col.ENDC}')

    def right_release(self, hwnd:int|None) -> None:
        if super().keyup(hwnd, self.RIGHT_KEYCODE):
            print(f'{col.OKCYAN}Right release sent to {hwnd}{col.ENDC}')