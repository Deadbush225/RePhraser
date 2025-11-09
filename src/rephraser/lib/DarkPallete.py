from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
import sys

from rephraser.lib.Logger import Logger

class DarkPalette(QPalette):
    def __init__(self):
        super().__init__()
        self.setColor(QPalette.Window, QColor(53, 53, 53))
        self.setColor(QPalette.WindowText, Qt.white)
        self.setColor(QPalette.Base, QColor(35, 35, 35))
        self.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        self.setColor(QPalette.ToolTipBase, QColor(25, 25, 25))
        self.setColor(QPalette.ToolTipText, Qt.white)
        self.setColor(QPalette.Text, Qt.white)
        self.setColor(QPalette.Button, QColor(53, 53, 53))
        self.setColor(QPalette.ButtonText, Qt.white)
        self.setColor(QPalette.BrightText, Qt.red)
        self.setColor(QPalette.Link, QColor(42, 130, 218))
        self.setColor(QPalette.Highlight, QColor(42, 130, 218))
        self.setColor(QPalette.HighlightedText, QColor(35, 35, 35))
        self.setColor(QPalette.Active, QPalette.Button, QColor(53, 53, 53))
        self.setColor(QPalette.Disabled, QPalette.ButtonText, Qt.darkGray)
        self.setColor(QPalette.Disabled, QPalette.WindowText, Qt.darkGray)
        self.setColor(QPalette.Disabled, QPalette.Text, Qt.darkGray)
        self.setColor(QPalette.Disabled, QPalette.Light, QColor(53, 53, 53))

def enable_dark_titlebar( window: QWidget):
    """Enable dark titlebar on Windows"""
    if sys.platform == 'win32':
        try:
            import ctypes
            from ctypes.wintypes import DWORD, BOOL, HRGN, HWND
            
            # Detect Windows version to use correct constant
            win_version = sys.getwindowsversion()
            if (win_version.major == 10 and win_version.build >= 17763) or win_version.major > 10:
                DWMWA_USE_IMMERSIVE_DARK_MODE = 20  # Windows 10 1809+
            else:
                DWMWA_USE_IMMERSIVE_DARK_MODE = 19  # Earlier Windows 10
            
            hwnd = HWND(window.winId().__int__())
            value = BOOL(True)
            
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 
                DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(value),
                ctypes.sizeof(value)
            )
            
            Logger.w("Dark titlebar enabled successfully", Logger.INFO)
        except Exception as e:
            Logger.w("Failed to set dark titlebar: {e}", Logger.WARNING)