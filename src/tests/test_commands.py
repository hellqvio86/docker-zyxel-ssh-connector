import argparse
from io import StringIO
from unittest.mock import patch

from zyxel_cli import commands


class FakeSession:
    def __init__(self):
        self.executed = []
        self.interactive_called = False
        self.next_output: str | None = None

    def execute_command(self, *, command: str):
        self.executed.append(command)
        if self.next_output is not None:
            return self.next_output
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
    ns.output_json = extra.get("output_json", False)
    return ns


def test_create_parser_contains_subcommands():
    p = commands.create_parser()
    # ensure parser recognizes known subcommands
    args = p.parse_args(["-H", "1.2.3.4", "version"])
    assert args.command == "version"


def test_handle_args_exec_calls_execute_and_returns_output():
    fake = FakeSession()
    with patch.object(commands, "ZyxelSession", new=lambda *a, **k: fake):
        with patch.object(commands, "resolve_password", new=lambda *a, **k: "pw"):
            args = make_args("exec", exec_command="show ip interface")
            out = commands.handle_args(args=args)

    assert out == "OUT: show ip interface"
    assert "show ip interface" in fake.executed


def test_handle_args_mapped_command():
    fake = FakeSession()
    with patch.object(commands, "ZyxelSession", new=lambda *a, **k: fake):
        with patch.object(commands, "resolve_password", new=lambda *a, **k: "pw"):
            args = make_args("version")
            out = commands.handle_args(args=args)

    assert out == "OUT: show version"
    assert fake.executed == ["show version"]


def test_handle_args_interactive_calls_session():
    fake = FakeSession()
    with patch.object(commands, "ZyxelSession", new=lambda *a, **k: fake):
        with patch.object(commands, "resolve_password", new=lambda *a, **k: "pw"):
            args = make_args("interactive")
            out = commands.handle_args(args=args)

    assert out is None
    assert fake.interactive_called is True


def test_handle_args_json_output():
    fake = FakeSession()
    fake.next_output = "Key : Value\nKey2 : Value2"
    stdout = StringIO()
    with patch.object(commands, "ZyxelSession", new=lambda *a, **k: fake):
        with patch.object(commands, "resolve_password", new=lambda *a, **k: "pw"):
            with patch("sys.stdout", new=stdout):
                args = make_args("version", output_json=True)
                commands.handle_args(args=args)

    captured = stdout.getvalue()
    assert '"Key": "Value"' in captured
    assert '"Key2": "Value2"' in captured
    assert "{" in captured
    assert "}" in captured


def test_handle_args_interfaces_iterates_through_ports():
    """Test that interfaces command iterates through port IDs until invalid."""

    # Track which commands are executed
    executed_commands = []

    class CustomFakeSession:
        def __init__(self):
            self.executed = []

        def execute_command(self, *, command: str):
            executed_commands.append(command)
            if "show interface 1" in command:
                return "GigabitEthernet1 is up"
            elif "show interface 2" in command:
                return "GigabitEthernet2 is down"
            elif "show interface 3" in command:
                return "Invalid port id"
            else:
                return "Invalid port id"

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    stdout = StringIO()
    with patch.object(commands, "ZyxelSession", new=lambda *a, **k: CustomFakeSession()):
        with patch.object(commands, "resolve_password", new=lambda *a, **k: "pw"):
            with patch("sys.stdout", new=stdout):
                args = make_args("interfaces")
                out = commands.handle_args(args=args)

    # Should have called show interface 1, 2, and 3
    assert "show interface 1" in executed_commands
    assert "show interface 2" in executed_commands
    assert "show interface 3" in executed_commands

    # Output should contain both interface outputs
    assert out is not None
    assert "GigabitEthernet1 is up" in out
    assert "GigabitEthernet2 is down" in out

    # Should have printed to stdout
    captured = stdout.getvalue()
    assert "Interface 1" in captured
    assert "Interface 2" in captured
