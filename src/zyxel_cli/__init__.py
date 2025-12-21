"""Zyxel CLI - SSH client for Zyxel GS1900 switches"""

__version__ = "0.1.0"

from .cli import main
from .client import ZyxelSession

__all__ = ["ZyxelSession", "main"]
