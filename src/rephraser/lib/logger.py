from rephraser import project_dir

from datetime import datetime
import os
import glob

class Logger:
    DEBUG = "Debug"
    INFO = "Info"
    WARNING = "Warn"
    ERROR = "Error"
    CRITICAL = "Crit"

    _file = None
    _initialized = False

    @classmethod
    def _init(cls):
        if not cls._initialized:
            cls.cleanup_old_logs()
            now = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
            logs_dir = f"{project_dir}\\logs"
            os.makedirs(logs_dir, exist_ok=True)
            cls._file = open(f"{logs_dir}\\{now}.txt", "x")
            cls._initialized = True

    @classmethod
    def cleanup_old_logs(cls, keep=0):
        logs_dir = f"{project_dir}\\logs"
        log_files = sorted(
            glob.glob(f"{logs_dir}\\*.txt"), key=os.path.getmtime, reverse=True
        )
        for old_log in log_files[keep:]:
            try:
                os.remove(old_log)
            except Exception:
                pass

    @classmethod
    def w(cls, message, level):
        if not cls._initialized:
            cls._init()
        cls._file.write(f"[{datetime.now().strftime('%H:%M:%S')}][{level}] {message}\n")
        cls._file.flush()

    @classmethod
    def close(cls):
        if cls._file:
            cls._file.close()
            cls._file = None
            cls._initialized = False

Logger._init()