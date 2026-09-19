"""__init__.py"""

import logging
from .src.connectors import check_kaggle_connection

logger = logging.getLogger(__name__)
logger.info(
    "Welcome to Mimi's Workspace! This is the main.py file at sub directory ./workspace containing custom reusuable architects/algorithms."
)

__all__ = ["check_kaggle_connection"]
