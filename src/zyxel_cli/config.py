"""Configuration helpers for zyxel_cli

This module centralizes resolution of credentials and environment-backed
configuration so the rest of the codebase stays small and testable.
"""

import getpass
import os


def resolve_password(*, password: str | None = None, user: str, host: str) -> str:
    """Resolve password from explicit argument, `PASSWORD` env, or prompt.

    Returns the resolved password string.
    """
    if password:
        return password

    env_pw = os.environ.get("PASSWORD")
    if env_pw:
        return env_pw

    return getpass.getpass(f"Password for {user}@{host}: ")
