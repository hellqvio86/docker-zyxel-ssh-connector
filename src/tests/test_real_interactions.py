import time
import pytest
from zyxel_cli.client import ZyxelSession
from tests.test_client import FakeShell, FakeClient

# Real-world data from user logs
# Mapped responses for specific commands
COMMAND_MAP = {
    "show version": [
        b"show version\r\n",
        b"Boot Version     : V2.00 | 07/08/2015\r\n",
        b"Firmware Version : V2.50(AAHK.0) | 10/21/2019\r\n",
        b"GS1900# "
    ],
    "show running-config": [
        b"show running-config\r\n",
        # Simulate some config content as the log just shows the command echo and then next log implies connection closed/new command?
        # Actually the log shows "output": "show running-config\r" 
        # But usually there is more. Let's stick to exactly what's in the log for now, 
        # but the log might be truncated or empty config? 
        # "output": "show running-config\r" suggests maybe it returns empty or just the echo?
        # Let's assume for a "show running-config" we usually expect more, but faithfully reproducing the log:
        b"Building configuration...\r\n", # Common in switches, though not in the snippet, adding a realistic placeholder line if needed, or just what is there.
        # The log says: "output": "show running-config\r"
        # It seems very short. Let's use that but maybe add a prompt to indicate finish if needed.
        # Wait, the log for "config" says: "output": "show running-config\r"
        # That looks like it might have failed to capture full output or it was empty. 
        # Let's use a standard response pattern for testing.
        b"hostname Switch\r\n",
        b"GS1900# "
    ],
    "show interface status": [
        b"show interface status\r\n",
        b"Invalid port id\r\n",
        b"GS1900# "
    ],
    "show vlan": [
        b"show vlan\r\n",
        b"  VID  |     VLAN Name    |        Untagged Ports        |        Tagged Ports          |  Type   \r\n",
        b"-------+------------------+------------------------------+------------------------------+---------\r\n",
        b"     1 |          default |                  1-24,lag1-8 |                          --- | Default \r\n",
        b"     2 |            ALARM |                          --- |                           23 | Static \r\n",
        b"     3 |      IOTInternet |                          --- |                         8,23 | Static \r\n",
        b"     5 |         LocalIOT |                          --- |                           23 | Static \r\n",
        b"     7 |        PANNA0007 |                          --- |                           23 | Static \r\n",
        b"GS1900# "
    ]
}

@pytest.fixture
def mock_session(monkeypatch):
    # Setup a session with a FakeClient and FakeShell that uses our map
    initial = [b"\r\nGS1900# \r\n"]
    shell = FakeShell(initial_chunks=initial, command_map=COMMAND_MAP)
    client = FakeClient(shell)
    
    session = ZyxelSession(host="zyxel.hellqvio.se", user="admin", password="password")
    session.client = client
    
    # Speed up sleeps
    monkeypatch.setattr(time, "sleep", lambda s: None)
    
    return session

def test_version_command(mock_session):
    out = mock_session.execute_command(command="show version")
    assert "Boot Version     : V2.00 | 07/08/2015" in out
    assert "Firmware Version : V2.50(AAHK.0) | 10/21/2019" in out

def test_interface_status_error(mock_session):
    out = mock_session.execute_command(command="show interface status")
    assert "Invalid port id" in out

def test_vlan_command(mock_session):
    out = mock_session.execute_command(command="show vlan")
    assert "VLAN Name" in out
    assert "IOTInternet" in out
    assert "PANNA0007" in out
    assert "Untagged Ports" in out

def test_unknown_command_returns_empty_or_timeout(mock_session):
    # If we send a command not in the map, it should result in empty/timeout behavior
    # with our simple mock, it just won't add response chunks, so it returns empty string
    out = mock_session.execute_command(command="show unknown")
    # depending on how execute_command handles empty response or timeout
    # currently it just collects what it gets.
    assert out == "" 
