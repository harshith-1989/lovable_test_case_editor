import logging
import sys
from colorama import Fore, Style, init as colorama_init

colorama_init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA,
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelno, "")
        formatted = super().format(record)
        return f"{log_color}{formatted}{Style.RESET_ALL}"


def get_logger(name: str, level=logging.INFO):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = ColoredFormatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False
    logger.setLevel(level)
    return logger
