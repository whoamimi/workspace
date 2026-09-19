"""workspace/main.py

Contains custom CLI Module for this workspace and serves as entry point for navigating around this Macbook's workspace.
"""

import logging
from datetime import datetime
from pathlib import Path

from _utils.logger import setup_logger

# Checks exec run is by correct path

cwd = Path().resolve()
timestamp = datetime.now()

if cwd.as_posix().endswith("Projects"):
    root_path = cwd
    output_dir = root_path / ".outputs"
    log_file_path = output_dir / "logs" / f"{timestamp.isoformat()}.log"
    print(f"Succesfully resolved all paths at cwd: {cwd}")
else:
    raise RuntimeError(f"Error resolving paths of cwd: {cwd}")


setup_logger(
    level=logging.DEBUG,
    log_file=log_file_path.as_posix(),
    show_caller=True,
    show_func=True,
)

logger = logging.getLogger(__name__)
logger.debug(
    "Welcome to Mimi's Workspace! Use this CLI tool to navigate around hackathons, projects and curious side-tracks!"
)
