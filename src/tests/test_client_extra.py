import getpass

import pytest

from zyxel_cli.client import ZyxelSession
from zyxel_cli.config import resolve_password


def test_password_arg_wins_over_env(monkeypatch):
    monkeypatch.setenv("PASSWORD", "envpw")
    pw = resolve_password(password="argpw", user="user", host="host")
    assert pw == "argpw"


def test_password_env_used_when_no_arg(monkeypatch):
    monkeypatch.setenv("PASSWORD", "envpw")
    pw = resolve_password(password=None, user="user", host="host")
    assert pw == "envpw"


def test_password_prompt_used_when_no_arg_or_env(monkeypatch):
    monkeypatch.delenv("PASSWORD", raising=False)
    monkeypatch.setattr(getpass, "getpass", lambda prompt: "promptpw")
    pw = resolve_password(password=None, user="user", host="host")
    assert pw == "promptpw"


def test_connect_raises_connectionerror_when_ssh_fails(monkeypatch):
    class FakeSSH:
        def set_missing_host_key_policy(self, p):
            pass

        def connect(self, **k):
            raise Exception("boom")

    monkeypatch.setattr("zyxel_cli.client.paramiko.SSHClient", lambda: FakeSSH())

    s = ZyxelSession(host="h", user="u", password="p")
    with pytest.raises(ConnectionError) as exc:
        s.connect()
    assert "Failed to connect to h" in str(exc.value)


def test_context_manager_calls_connect_and_close(monkeypatch):
    called = {"connect": False, "close": False}

    def fake_connect(self):
        called["connect"] = True

    def fake_close(self):
        called["close"] = True

    monkeypatch.setattr("zyxel_cli.client.ZyxelSession.connect", fake_connect)
    monkeypatch.setattr("zyxel_cli.client.ZyxelSession.close", fake_close)

    with ZyxelSession(host="h", user="u", password="p") as s:
        assert called["connect"] is True

    assert called["close"] is True


def test_execute_command_raises_when_not_connected():
    s = ZyxelSession(host="h", user="u", password="p")
    s.client = None
    with pytest.raises(RuntimeError):
        s.execute_command(command="show version")


def test_interactive_exits_on_eof(monkeypatch):
    class FakeShell:
        def settimeout(self, t):
            pass

        def recv(self, n):
            return b""

        def send(self, data):
            pass

    class FakeClient:
        def invoke_shell(self):
            return FakeShell()

    s = ZyxelSession(host="h", user="u", password="p")
    s.client = FakeClient()  # type: ignore[assignment]

    # Monkeypatch termios/tty/select in the module namespace to avoid touching real terminal
    import zyxel_cli.client as client_mod

    class FakeTermios:
        TCSADRAIN = 0

        @staticmethod
        def tcgetattr(stdin):
            return "old"

        @staticmethod
        def tcsetattr(stdin, when, old):
            return None

    class FakeTty:
        @staticmethod
        def setraw(fd):
            return None

        @staticmethod
        def setcbreak(fd):
            return None

    # Inject fake termios/tty/select modules into sys.modules so local imports pick them up
    import sys as _sys

    monkeypatch.setitem(_sys.modules, "termios", FakeTermios)
    monkeypatch.setitem(_sys.modules, "tty", FakeTty)

    class FakeStdin:
        def fileno(self):
            return 0

        def read(self, n=1):
            return ""  # simulate EOF to break loop

    fake_stdin = FakeStdin()

    class FakeSelect:
        @staticmethod
        def select(r, w, e):
            return ([fake_stdin], [], [])

    monkeypatch.setitem(_sys.modules, "select", FakeSelect)

    import zyxel_cli.client as client_mod2

    monkeypatch.setattr(client_mod2.sys, "stdin", fake_stdin)

    # Should not raise
    s.interactive()
