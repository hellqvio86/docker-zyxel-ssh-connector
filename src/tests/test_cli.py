import sys
from io import StringIO

import pytest

from zyxel_cli import cli


def test_main_no_command_exits(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["zyxel-cli", "-H", "1.2.3.4"])
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 1


def test_main_exec_uses_session(monkeypatch, capsys):
    # Fake ZyxelSession context manager
    class FakeSession:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            return False

        def execute_command(self, *, command):
            return "RESULT: " + command

    monkeypatch.setattr(
        sys,
        "argv",
        ["zyxel-cli", "-H", "1.2.3.4", "-u", "admin", "-p", "pw", "exec", "show version"],
    )
    monkeypatch.setattr("zyxel_cli.commands.ZyxelSession", lambda *a, **k: FakeSession())

    out = StringIO()
    monkeypatch.setattr("sys.stdout", out)

    cli.main()

    output = out.getvalue()
    assert "RESULT: show version" in output
