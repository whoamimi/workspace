"""
app/utils/logger.py
"""

import logging
import sys
from pathlib import Path


class BotnetLogger(logging.Formatter):
    """Custom Logger formatter with pastel colors and caller info"""

    # Colors
    RESET = "\033[0m"
    COLORS = {
        "DEBUG": "\033[38;5;153m",  # Powder blue
        "INFO": "\033[38;5;158m",  # Mint
        "WARNING": "\033[38;5;223m",  # Peach
        "ERROR": "\033[38;5;210m",  # Coral
        "CRITICAL": "\033[1m\033[38;5;211m",  # Bold rose
        "time": "\033[2m\033[38;5;245m",  # Dim gray
        "caller": "\033[38;5;183m",  # Lavender
        "func": "\033[38;5;218m",  # Pink
        "msg": "\033[38;5;255m",  # White
    }

    def __init__(self, use_colors=True, show_caller=True, show_func=True):
        super().__init__(datefmt="%Y-%m-%d %H:%M:%S")
        self.use_colors = use_colors
        self.show_caller = show_caller
        self.show_func = show_func
        self.root = Path.cwd()

    def format(self, record):
        # Level
        level = f"{record.levelname.upper():<8}"
        if self.use_colors:
            level = f"{self.COLORS.get(record.levelname, '')}{level}{self.RESET}"

        # Timestamp
        time = self.formatTime(record, self.datefmt)
        if self.use_colors:
            time = f"{self.COLORS['time']}{time}{self.RESET}"

        # Caller info
        caller_parts = []
        if self.show_caller:
            try:
                rel_path = Path(record.pathname).relative_to(self.root)
            except ValueError:
                rel_path = Path(record.pathname).name
            caller = f"{rel_path}:{record.lineno}"
            if self.use_colors:
                caller = f"{self.COLORS['caller']}{caller}{self.RESET}"
            caller_parts.append(caller)

        if self.show_func:
            func = record.funcName if record.funcName != "<module>" else "module"
            if self.use_colors:
                func = f"{self.COLORS['func']}{func}(){self.RESET}"
            else:
                func = f"{func}()"
            caller_parts.append(func)

        caller_info = f" [{' → '.join(caller_parts)}]" if caller_parts else ""

        # Message
        msg = record.getMessage()
        if self.use_colors:
            msg = f"{self.COLORS['msg']}{msg}{self.RESET}"

        # Combine
        log_line = f"{level}:  {time}{caller_info} {msg}"

        # Add exception if present
        if record.exc_info:
            log_line += "\n" + self.formatException(record.exc_info)

        return log_line


def setup_logger(level=logging.INFO, log_file=None, show_caller=True, show_func=True):
    """
    Setup pastel logger with uvicorn-style formatting.
    Call this once at application startup.

    Args:
        level: Logging level (e.g., logging.DEBUG, logging.INFO)
        log_file: Optional file path for logging
        show_caller: Show script path and line number
        show_func: Show function name

    Returns:
        Root logger instance
    """
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(
        BotnetLogger(use_colors=True, show_caller=show_caller, show_func=show_func)
    )
    root.addHandler(console)

    # File handler (optional)
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            BotnetLogger(use_colors=False, show_caller=show_caller, show_func=show_func)
        )
        root.addHandler(file_handler)

    # Mount all existing loggers
    for name in logging.Logger.manager.loggerDict:
        logger = logging.getLogger(name)
        logger.handlers.clear()
        logger.propagate = True
        logger.setLevel(logging.NOTSET)

    return root
