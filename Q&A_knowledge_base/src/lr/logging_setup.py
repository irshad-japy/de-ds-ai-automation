import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from .config import settings

def setup_logging() -> None:
    Path(settings.log_dir).mkdir(parents=True, exist_ok=True)
    log_path = Path(settings.log_dir) / "app.log"

    fmt = logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
    root = logging.getLogger()
    root.setLevel(settings.log_level)

    # console
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    root.addHandler(ch)

    # rotating file (no cloud costs)
    fh = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=3, encoding="utf-8")
    fh.setFormatter(fmt)
    root.addHandler(fh)
