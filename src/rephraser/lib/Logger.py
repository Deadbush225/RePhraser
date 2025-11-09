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
            logs_dir = project_dir / "logs"
            logs_dir.mkdir(parents=True, exist_ok=True)
            cls._file = open(logs_dir / f"{now}.txt", "x")
            cls._initialized = True

    @classmethod
    def cleanup_old_logs(cls, keep=0):
        logs_dir = project_dir / "logs"
        log_files = sorted(logs_dir.glob("*.txt"), key=os.path.getmtime, reverse=True)
        for old_log in log_files[keep:]:
            try:
                old_log.unlink()
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
