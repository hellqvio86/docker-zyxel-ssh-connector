"""Zyxel CLI - SSH client for Zyxel GS1900 switches"""

__version__ = "0.1.0"

from .client import ZyxelSession
from .cli import main

__all__ = ["ZyxelSession", "main"]
