import argparse
from io import StringIO

import pytest

from zyxel_cli import commands


class FakeSession:
    def __init__(self):
        self.executed = []
        self.interactive_called = False

    def execute_command(self, *, command: str):
        self.executed.append(command)
        return f"OUT: {command}"

    def interactive(self):
        self.interactive_called = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def make_args(cmd: str, **extra) -> argparse.Namespace:
    ns = argparse.Namespace()
    ns.host = extra.get("host", "1.2.3.4")
    ns.user = extra.get("user", "admin")
    ns.password = extra.get("password", None)
    ns.port = extra.get("port", 22)
    ns.command = cmd
    ns.exec_command = extra.get("exec_command", "")
    ns.debug = extra.get("debug", False)
    return ns


def test_create_parser_contains_subcommands():
    p = commands.create_parser()
    # ensure parser recognizes known subcommands
    args = p.parse_args(["-H", "1.2.3.4", "version"])
    assert args.command == "version"


def test_handle_args_exec_calls_execute_and_returns_output(monkeypatch):
    fake = FakeSession()
    monkeypatch.setattr(commands, "ZyxelSession", lambda *a, **k: fake)
    monkeypatch.setattr(commands, "resolve_password", lambda *a, **k: "pw")

    args = make_args("exec", exec_command="show ip interface")

    out = commands.handle_args(args=args)

    assert out == "OUT: show ip interface"
    assert "show ip interface" in fake.executed


def test_handle_args_mapped_command(monkeypatch, capsys):
    fake = FakeSession()
    monkeypatch.setattr(commands, "ZyxelSession", lambda *a, **k: fake)
    monkeypatch.setattr(commands, "resolve_password", lambda *a, **k: "pw")

    args = make_args("version")

    out = commands.handle_args(args=args)

    assert out == "OUT: show version"
    assert fake.executed == ["show version"]


def test_handle_args_interactive_calls_session(monkeypatch):
    fake = FakeSession()
    monkeypatch.setattr(commands, "ZyxelSession", lambda *a, **k: fake)
    monkeypatch.setattr(commands, "resolve_password", lambda *a, **k: "pw")

    args = make_args("interactive")

    out = commands.handle_args(args=args)

    assert out is None
    assert fake.interactive_called is True
