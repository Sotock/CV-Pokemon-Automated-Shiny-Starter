import ctypes
import sys
from ctypes import wintypes


def apply_window_style(window):

    if sys.platform != "win32":

        return

    window.update_idletasks()

    try:

        user32 = ctypes.windll.user32
        dwmapi = ctypes.windll.dwmapi

        user32.GetAncestor.argtypes = [
            wintypes.HWND,
            wintypes.UINT
        ]

        user32.GetAncestor.restype = wintypes.HWND

        hwnd = user32.GetAncestor(
            window.winfo_id(),
            2
        )

        if not hwnd:

            return

        set_attribute = dwmapi.DwmSetWindowAttribute

        set_attribute.argtypes = [
            wintypes.HWND,
            wintypes.DWORD,
            ctypes.c_void_p,
            wintypes.DWORD
        ]

        set_attribute.restype = ctypes.c_long

        attributes = {
            34: "#363C46",
            35: "#C5C8CE",
            36: "#17191D"
        }

        for attribute, color in attributes.items():

            red = int(color[1:3], 16)
            green = int(color[3:5], 16)
            blue = int(color[5:7], 16)

            color_value = ctypes.c_uint32(
                red | (green << 8) | (blue << 16)
            )

            set_attribute(
                hwnd,
                attribute,
                ctypes.byref(color_value),
                ctypes.sizeof(color_value)
            )

    except (AttributeError, OSError):

        pass