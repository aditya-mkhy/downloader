import ctypes
from threading import Thread
import win32clipboard
import win32gui
import win32con

# WinAPI
user32 = ctypes.windll.user32
AddClipboardFormatListener = user32.AddClipboardFormatListener
RemoveClipboardFormatListener = user32.RemoveClipboardFormatListener

WM_CLIPBOARDUPDATE = 0x031D

class ClipboardWatcher(Thread):
    def __init__(self, callback):
        super().__init__(daemon=True)
        self.callback = callback
        self.hwnd = None

    def run(self):
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self._wnd_proc
        wc.lpszClassName = "ClipboardWatcherThread"
        class_atom = win32gui.RegisterClass(wc)

        self.hwnd = win32gui.CreateWindow(
            class_atom,
            "Clipboard Watcher",
            0,
            0, 0, 0, 0,
            0, 0, 0, None
        )

        AddClipboardFormatListener(self.hwnd)
        win32gui.PumpMessages()

    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == WM_CLIPBOARDUPDATE:
            self._on_clipboard_change()
        elif msg == win32con.WM_DESTROY:
            win32gui.PostQuitMessage(0)
        return 0

    def _on_clipboard_change(self):
        try:
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            self.callback(data)
        except Exception:
            pass

    def stop(self):
        if self.hwnd:
            RemoveClipboardFormatListener(self.hwnd)
            win32gui.PostMessage(self.hwnd, win32con.WM_DESTROY, 0, 0)


def on_copy(data):
    print("Copied:", data)


if __name__ == "__main__":
    from time import sleep
    watcher = ClipboardWatcher(on_copy)
    watcher.start()

    # Your existing download loop
    while True:
        sleep(0.5)
