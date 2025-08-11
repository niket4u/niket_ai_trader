
import logging, os, datetime, glob, shutil
from .config import settings

def ensure_log_dir():
    os.makedirs(settings.log_dir, exist_ok=True)
    return settings.log_dir

def cleanup_old_logs():
    # delete files older than retention days
    cutoff = datetime.datetime.now() - datetime.timedelta(days=settings.log_retention_days)
    for path in glob.glob(os.path.join(settings.log_dir, "*.log")):
        try:
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path))
            if mtime < cutoff:
                os.remove(path)
        except Exception:
            pass

def get_logger(name: str) -> logging.Logger:
    ensure_log_dir()
    cleanup_old_logs()

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    level = settings.log_level.upper()
    logger.setLevel(getattr(logging, level, logging.INFO))

    log_path = os.path.join(settings.log_dir, datetime.datetime.now().strftime("%Y-%m-%d") + ".log")
    fh = logging.FileHandler(log_path)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    return logger
