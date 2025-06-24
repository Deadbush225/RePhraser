from rephraser import project_dir

from datetime import datetime
from enum import Enum, auto
import os
import glob

# os.path.exists(f"{project_dir}\\logs\\{now}.txt")

class LogLevel(Enum):
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()

    def __str__(self):
        custom_strings = {
            LogLevel.DEBUG: "Debug",
            LogLevel.INFO: "Info",
            LogLevel.WARNING: "Warning",
            LogLevel.ERROR: "Error",
            LogLevel.CRITICAL: "Critical"
        }
        return custom_strings.get(self, self.name)

class Logger:     
    def __init__(self):
        self.cleanup_old_logs()
        now = datetime.now().strftime("%Y-%m-d %H-%M-%S")
        self.file = open(f"{project_dir}\\logs\\{now}.txt", "x")
    
    def cleanup_old_logs(self, keep=0):
        logs_dir = f"{project_dir}\\logs"
        log_files = sorted(
            glob.glob(f"{logs_dir}\\*.txt"),
            key=os.path.getmtime,
            reverse=True
        )
        for old_log in log_files[keep:]:
            try:
                os.remove(old_log)
            except Exception:
                pass

    def w(self, message, level):
        self.file.write(f"[{datetime.now().strftime('%H:%M:%S')}][{level}] {message}\n")
        self.file.flush()

    def __del__(self):
        self.file.close()

log = Logger()