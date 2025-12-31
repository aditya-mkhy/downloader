import ctypes
import win32clipboard
import win32gui
import win32con

# ---- WinAPI via ctypes ----
user32 = ctypes.windll.user32
AddClipboardFormatListener = user32.AddClipboardFormatListener
RemoveClipboardFormatListener = user32.RemoveClipboardFormatListener

# ---- Missing constant (pywin32 bug) ----
WM_CLIPBOARDUPDATE = 0x031D

class ClipboardWatcher:
    def __init__(self):
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self._wnd_proc
        wc.lpszClassName = "ClipboardWatcher"
        self.classAtom = win32gui.RegisterClass(wc)

        self.hwnd = win32gui.CreateWindow(
            self.classAtom,
            "Clipboard Watcher",
            0,
            0, 0, 0, 0,
            0, 0, 0, None
        )

        AddClipboardFormatListener(self.hwnd)

    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == WM_CLIPBOARDUPDATE:
            self.on_clipboard_change()
        elif msg == win32con.WM_DESTROY:
            win32gui.PostQuitMessage(0)
        return 0

    def on_clipboard_change(self):
        try:
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            print("Copied:", data)
        except Exception:
            pass

    def cleanup(self):
        RemoveClipboardFormatListener(self.hwnd)
        win32gui.DestroyWindow(self.hwnd)


if __name__ == "__main__":
    watcher = ClipboardWatcher()
    win32gui.PumpMessages()
