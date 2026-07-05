from __future__ import annotations

import ctypes
import os
from ctypes import wintypes
from typing import Callable


def enable_file_drop(widget, callback: Callable[[list[str]], None]) -> bool:
    if os.name != "nt":
        return False
    try:
        widget.update_idletasks()
        hwnd = widget.winfo_id()
        user32 = ctypes.windll.user32
        shell32 = ctypes.windll.shell32
        WM_DROPFILES = 0x0233
        GWL_WNDPROC = -4

        WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_longlong, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)

        SetWindowLongPtr = getattr(user32, "SetWindowLongPtrW", user32.SetWindowLongW)
        GetWindowLongPtr = getattr(user32, "GetWindowLongPtrW", user32.GetWindowLongW)
        CallWindowProc = user32.CallWindowProcW

        GetWindowLongPtr.argtypes = [wintypes.HWND, ctypes.c_int]
        GetWindowLongPtr.restype = ctypes.c_longlong
        SetWindowLongPtr.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_longlong]
        SetWindowLongPtr.restype = ctypes.c_longlong
        CallWindowProc.argtypes = [ctypes.c_longlong, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
        CallWindowProc.restype = ctypes.c_longlong

        old_proc = GetWindowLongPtr(hwnd, GWL_WNDPROC)

        def query_files(hdrop) -> list[str]:
            count = shell32.DragQueryFileW(hdrop, 0xFFFFFFFF, None, 0)
            files: list[str] = []
            for index in range(count):
                length = shell32.DragQueryFileW(hdrop, index, None, 0)
                buffer = ctypes.create_unicode_buffer(length + 1)
                shell32.DragQueryFileW(hdrop, index, buffer, length + 1)
                files.append(buffer.value)
            shell32.DragFinish(hdrop)
            return files

        def wnd_proc(window, message, wparam, lparam):
            if message == WM_DROPFILES:
                files = query_files(wparam)
                widget.after(0, lambda: callback(files))
                return 0
            return CallWindowProc(old_proc, window, message, wparam, lparam)

        proc = WNDPROC(wnd_proc)
        SetWindowLongPtr(hwnd, GWL_WNDPROC, ctypes.cast(proc, ctypes.c_void_p).value)
        shell32.DragAcceptFiles(hwnd, True)
        widget._quickdrop_wndproc = proc
        widget._quickdrop_old_wndproc = old_proc
        return True
    except Exception:
        return False
