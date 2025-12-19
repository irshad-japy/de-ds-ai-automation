import os
import sys
import json
import logging
from logging.handlers import RotatingFileHandler
from decimal import Decimal
from pathlib import Path
from datetime import datetime, timezone, timedelta
LOG_ID = "ID"
LOG_TS = "TS"
LOG_CONTEXT = "Context"

# ────────────────────────────────────────────────────────────────────────────────
# Utility Functions
# ────────────────────────────────────────────────────────────────────────────────
def _convert_decimals(obj):
    if isinstance(obj, list):
        return [_convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: _convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return str(obj)
    else:
        return obj

def create_json_log(**kwargs):
    log_entry = {}
    if LOG_ID not in kwargs and kwargs.get(LOG_CONTEXT) is not None:
        kwargs[LOG_ID] = kwargs[LOG_CONTEXT].get(LOG_ID)
    for key, value in kwargs.items():
        if value is not None:
            log_entry[key] = value
    log_entry = _convert_decimals(log_entry)
    return json.dumps(log_entry)

def log_message(**kwargs):
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
    if LOG_TS not in kwargs:
        kwargs[LOG_TS] = timestamp
    return create_json_log(**kwargs)

# ────────────────────────────────────────────────────────────────────────────────
# Custom Rotating File Handler
# ────────────────────────────────────────────────────────────────────────────────
class CustomRotatingFileHandler(RotatingFileHandler):
    """
    Rotating file handler that:
    - Uses names like: base_name_YYYYMMDD_index.log
    - Rotates when maxBytes is exceeded
    - Cleans up log files older than `days_to_keep` (default 30)
    """

    def __init__(
        self,
        base_name: str,
        log_dir: str = None,
        maxBytes: int = 5 * 1024 * 1024,
        backupCount: int = 5,
        days_to_keep: int = 30,
        **kwargs,
    ):
        self.base_name = base_name
        self.log_dir = log_dir or os.getcwd()
        self.days_to_keep = days_to_keep

        os.makedirs(self.log_dir, exist_ok=True)

        self.current_time = datetime.now().strftime("%Y%m%d")
        self.rotation_count = 0

        # track last cleanup to avoid doing it too often if you want
        self._last_cleanup = None

        filename = os.path.join(self.log_dir, self._make_filename())
        super().__init__(
            filename,
            maxBytes=maxBytes,
            backupCount=backupCount,
            encoding="utf-8",
            **kwargs,
        )

        # NEW: run cleanup once at startup
        self._cleanup_old_logs()

    def _make_filename(self, date_str: str = None, index: int = None) -> str:
        date_str = date_str or self.current_time
        index = self.rotation_count if index is None else index
        return f"{self.base_name}_{date_str}_{index}.log"

    def doRollover(self):
        """
        Called when the log file should rollover.
        """
        if self.stream:
            self.stream.close()
            self.stream = None

        # Update date & rotation index
        now_date = datetime.now().strftime("%Y%m%d")
        if now_date != self.current_time:
            self.current_time = now_date
            self.rotation_count = 0
        else:
            self.rotation_count += 1

        # Rotate current file if it exists
        if os.path.exists(self.baseFilename):
            rotated = os.path.join(self.log_dir, self._make_filename())
            os.rename(self.baseFilename, rotated)

        # New base filename
        self.baseFilename = os.path.join(self.log_dir, self._make_filename())
        self.stream = self._open()

        # Cleanup old logs after each rollover
        self._cleanup_old_logs()

    def _cleanup_old_logs(self):
        """
        Delete log files older than `days_to_keep` days
        for this base_name in log_dir.

        Tries date from filename (base_YYYYMMDD_x.log),
        falls back to file mtime if parsing fails.
        """
        now = datetime.now()
        cutoff = now - timedelta(days=self.days_to_keep)

        for path in Path(self.log_dir).glob(f"{self.base_name}_*.log"):
            name = path.name
            # Expected pattern: base_name_YYYYMMDD_index.log
            parts = name.split("_")
            dt = None

            if len(parts) >= 3:
                date_str = parts[-2]
                try:
                    dt = datetime.strptime(date_str, "%Y%m%d")
                except ValueError:
                    dt = None

            # Fallback: use filesystem modification time
            if dt is None:
                dt = datetime.fromtimestamp(path.stat().st_mtime)

            if dt < cutoff:
                try:
                    path.unlink()
                except OSError:
                    # Ignore delete failures
                    pass

# ────────────────────────────────────────────────────────────────────────────────
# Logger Getter Function
# ────────────────────────────────────────────────────────────────────────────────
def get_logger(module_name, log_level=logging.INFO, log_dir='logs'):
    """
    Retrieve a logger configured for a specific module.

    - Logs to console AND to a rotating file.
    - If log_dir is None, logs are stored in this file's directory.
    """
    logger = logging.getLogger(module_name)
    logger.setLevel(log_level)
    logger.propagate = False

    # If already configured, just return it
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s - Line: %(lineno)d'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Decide log directory
    if log_dir is None:
        log_dir = os.path.dirname(os.path.abspath(__file__))

    # File handler (5MB, keep 5 rotations, cleanup >30 days)
    file_handler = CustomRotatingFileHandler(
        base_name=module_name,
        log_dir=log_dir,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        days_to_keep=30,
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# ────────────────────────────────────────────────────────────────────────────────
# Demo Test Block
# ────────────────────────────────────────────────────────────────────────────────
# if __name__ == "__main__":
#     logger = get_logger("test_module", logging.DEBUG)
#     logger.info(log_message(
#         log_level="INFO",
#         log_message="Sample test log",
#         log_context={"user": "irshad", "action": "demo"}
#     ))