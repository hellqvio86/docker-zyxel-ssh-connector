import time

import pytest

from zyxel_cli.client import ZyxelSession


def test_clean_output_removes_ansi_and_prompts():
    raw = "\x1b[31mHello\x1b[0m\nSwitch> show version\nVersion 1.2.3\n"
    cleaned = ZyxelSession._clean_output(raw)
    assert "Hello" in cleaned
    assert "Version 1.2.3" in cleaned
    assert "Switch>" not in cleaned


class FakeShell:
    def __init__(self, initial_chunks=None, response_chunks=None):
        self.initial_chunks = initial_chunks or []
        self.response_chunks = response_chunks or []
        self.sent = []
        self.closed = False
        self._produced_response = False

    def recv_ready(self):
        if not self._produced_response and self.initial_chunks:
            return True
        return bool(self.response_chunks)

    def recv(self, n):
        if not self._produced_response and self.initial_chunks:
            return self.initial_chunks.pop(0)
        if self.response_chunks:
            return self.response_chunks.pop(0)
        return b""

    def send(self, data):
        self.sent.append(data)
        # When command is sent, make responses available
        if data and data.strip():
            self._produced_response = True

    def close(self):
        self.closed = True


class FakeClient:
    def __init__(self, shell):
        self._shell = shell

    def invoke_shell(self):
        return self._shell

    def close(self):
        pass


def test_execute_command_collects_output(monkeypatch):
    # Arrange: fake shell will have an initial prompt and then output after command
    initial = [b"\r\nSwitch>\r\n"]
    response = [b"Output line 1\r\n", b"Output line 2\r\n"]
    shell = FakeShell(initial_chunks=initial, response_chunks=response)
    client = FakeClient(shell)

    session = ZyxelSession(host="host", user="user", password="pass")
    session.client = client  # type: ignore[assignment]

    # Speed up sleeps
    monkeypatch.setattr(time, "sleep", lambda s: None)

    out = session.execute_command(command="show version")

    # At least the response should contain expected data
    assert "Output line 2" in out
    assert shell.closed is True
