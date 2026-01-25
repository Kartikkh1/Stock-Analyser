import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger('stock_analyser')
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers if setup_logging is called multiple times.
    if logger.handlers:
        return logger

    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    max_bytes = int(os.getenv("LOG_MAX_BYTES", "2097152"))  # 2 MB
    backup_count = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    log_path = os.path.join(log_dir, 'stock_analyser.log')

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setFormatter(log_format)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_format)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.propagate = False

    return logger

logger = setup_logging()
