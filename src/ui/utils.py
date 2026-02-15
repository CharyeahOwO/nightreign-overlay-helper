from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt
from src.logger import info, warning, error


def set_widget_always_on_top(widget: QWidget):
    try:
        import win32gui
        import win32con
        hwnd = widget.winId().__int__()
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 
                                0, 0, 0, 0, 
                                win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
        info(f"Window HWND: {hwnd} set to TOPMOST.")
    except Exception as e:
        warning(f"Error setting system always on top: {e}")


def set_window_exstyle(hwnd: int, add_flags: int = 0, remove_flags: int = 0) -> bool:
    try:
        import win32gui
        import win32con
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        style = (style | add_flags) & ~remove_flags
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style)
        win32gui.SetWindowPos(
            hwnd,
            0,
            0,
            0,
            0,
            0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOZORDER | win32con.SWP_FRAMECHANGED,
        )
        return True
    except Exception as e:
        warning(f"Error setting window exstyle: {e}")
        return False


def set_window_display_affinity(hwnd: int, affinity: int) -> bool:
    try:
        import win32gui
        win32gui.SetWindowDisplayAffinity(hwnd, affinity)
        return True
    except Exception as e:
        warning(f"Error setting window display affinity: {e}")
        return False


def set_dwm_excluded_from_capture(hwnd: int, excluded: bool) -> bool:
    try:
        import ctypes

        DWMWA_EXCLUDED_FROM_CAPTURE = 33
        value = ctypes.c_int(1 if excluded else 0)
        res = ctypes.windll.dwmapi.DwmSetWindowAttribute(
            ctypes.c_void_p(hwnd),
            ctypes.c_uint(DWMWA_EXCLUDED_FROM_CAPTURE),
            ctypes.byref(value),
            ctypes.sizeof(value),
        )
        return res == 0
    except Exception as e:
        warning(f"Error setting DWM excluded-from-capture: {e}")
        return False


def apply_window_compatibility(widget: QWidget, config) -> None:
    if not getattr(config, "lossless_scaling_compat_mode", False):
        return
    hwnd = widget.winId().__int__()
    add_flags = 0
    remove_flags = 0
    try:
        import win32con
        add_flags |= win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOOLWINDOW
        remove_flags |= win32con.WS_EX_APPWINDOW
        if getattr(config, "overlay_no_redirection_bitmap", False):
            add_flags |= win32con.WS_EX_NOREDIRECTIONBITMAP
        if getattr(config, "overlay_input_passthrough", False):
            add_flags |= win32con.WS_EX_TRANSPARENT
    except Exception as e:
        warning(f"Error preparing window compatibility flags: {e}")
    if add_flags or remove_flags:
        set_window_exstyle(hwnd, add_flags=add_flags, remove_flags=remove_flags)
    if getattr(config, "overlay_exclude_from_capture", False):
        set_window_display_affinity(hwnd, 0x11)
        set_dwm_excluded_from_capture(hwnd, True)


def is_window_in_foreground(window_title: str) -> bool:
    """
    检查包含特定标题的窗口是否在 Windows 的最前面。
    """
    try:
        import win32gui
        import time
        active_window_handle = win32gui.GetForegroundWindow()
        active_window_title = win32gui.GetWindowText(active_window_handle)
        if window_title.lower() in active_window_title.lower():
            return True
        return False
    except Exception as e:
        return False


def get_qt_screen_by_mss_region(region: tuple[int]) -> QWidget:
    """
    根据mss的region获取对应的QScreen对象。
    """
    x, y, w, h = region
    app: QApplication = QApplication.instance()
    screens = app.screens()
    for screen in screens:
        sx = screen.geometry().x()
        sy = screen.geometry().y()
        sw = screen.geometry().width()
        sh = screen.geometry().height()
        ratio = screen.devicePixelRatio()
        mss_sw = int(sw * ratio)
        mss_sh = int(sh * ratio)
        if sx <= x <= sx + mss_sw and sy <= y <= sy + mss_sh:
            return screen
    raise ValueError(f"Region {region} is out of all screen bounds")


def mss_region_to_qt_region(region: tuple[int]):
    screen = get_qt_screen_by_mss_region(region)
    x, y, w, h = region
    sx = screen.geometry().x()
    sy = screen.geometry().y()
    ratio = screen.devicePixelRatio()
    qx = sx + int((x - sx) / ratio)
    qy = sy + int((y - sy) / ratio)
    qw = int(w / ratio)
    qh = int(h / ratio)
    return (qx, qy, qw, qh)

    

def process_region_to_adapt_scale(region: tuple[int], scale: float) -> tuple[int]:
    """
    处理一个region的大小，使其能够适配指定的缩放比例。
    即 w/scale, h/scale为整数。
    """
    x, y, w, h = region
    new_w = int(int(w / scale) * scale)
    new_h = int(int(h / scale) * scale)
    return [x, y, new_w, new_h]
