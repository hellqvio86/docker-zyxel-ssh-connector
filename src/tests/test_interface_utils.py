"""Tests for interface_utils module."""

import pytest

from zyxel_cli.interface_utils import (
    collect_all_interfaces,
    is_invalid_port_response,
    parse_interface_output,
)


def test_is_invalid_port_response_detects_invalid():
    """Test that 'Invalid port id' is correctly detected."""
    output = "Invalid port id"
    assert is_invalid_port_response(output) is True


def test_is_invalid_port_response_detects_invalid_with_other_text():
    """Test detection when 'Invalid port id' appears with other text."""
    output = "GS1900# show interface 40\nInvalid port id\n"
    assert is_invalid_port_response(output) is True


def test_is_invalid_port_response_valid_output():
    """Test that valid interface output doesn't trigger invalid detection."""
    output = """GigabitEthernet1 is up
  Hardware is Gigabit Ethernet
  Auto-duplex, Auto-speed, media type is Copper
  flow-control is off
     1059016090 packets input, 2902879441 bytes, 0 throttles"""
    assert is_invalid_port_response(output) is False


def test_collect_all_interfaces_single_port():
    """Test collection with only 1 valid port."""
    call_count = 0

    def mock_execute(cmd: str) -> str:
        nonlocal call_count
        call_count += 1
        if "show interface 1" in cmd:
            return "GigabitEthernet1 is up"
        else:
            return "Invalid port id"

    result = collect_all_interfaces(mock_execute)

    assert len(result) == 1
    assert result[0] == (1, "GigabitEthernet1 is up")
    assert call_count == 2  # Called for port 1 and port 2


def test_collect_all_interfaces_multiple_ports():
    """Test collection with multiple valid ports."""

    def mock_execute(cmd: str) -> str:
        if "show interface 1" in cmd:
            return "GigabitEthernet1 is up"
        elif "show interface 2" in cmd:
            return "GigabitEthernet2 is down"
        elif "show interface 3" in cmd:
            return "GigabitEthernet3 is up"
        else:
            return "Invalid port id"

    result = collect_all_interfaces(mock_execute)

    assert len(result) == 3
    assert result[0] == (1, "GigabitEthernet1 is up")
    assert result[1] == (2, "GigabitEthernet2 is down")
    assert result[2] == (3, "GigabitEthernet3 is up")


def test_collect_all_interfaces_stops_at_first_invalid():
    """Test that iteration stops at first invalid port."""
    call_count = 0

    def mock_execute(cmd: str) -> str:
        nonlocal call_count
        call_count += 1
        if "show interface 1" in cmd:
            return "GigabitEthernet1 is up"
        elif "show interface 2" in cmd:
            return "GigabitEthernet2 is up"
        else:
            # Port 3 onwards are invalid
            return "Invalid port id"

    result = collect_all_interfaces(mock_execute)

    assert len(result) == 2
    assert call_count == 3  # Called for ports 1, 2, and 3 (which returned invalid)


def test_collect_all_interfaces_with_lag_ports():
    """Test collection including LAG ports (as shown in GS1900.MD)."""

    def mock_execute(cmd: str) -> str:
        port_outputs = {
            1: "GigabitEthernet1 is up\n  Hardware is Gigabit Ethernet",
            29: "LAG5 is down\n  Hardware is Fast Ethernet",
            30: "LAG6 is down\n  Hardware is Fast Ethernet",
        }

        # Extract port number from command
        import re

        match = re.search(r"show interface (\d+)", cmd)
        if match:
            port_num = int(match.group(1))
            if port_num in port_outputs:
                return port_outputs[port_num]
            elif port_num < 40:
                # Simulate gaps in port IDs - some ports exist, some don't
                # But we stop at first invalid
                if port_num <= 30:
                    return f"Port{port_num} output"
                else:
                    return "Invalid port id"
        return "Invalid port id"

    result = collect_all_interfaces(mock_execute)

    # Should collect all ports from 1 to 30, then stop at 31
    assert len(result) == 30
    assert result[0][0] == 1
    assert result[28][0] == 29
    assert result[29][0] == 30


def test_collect_all_interfaces_empty_when_first_is_invalid():
    """Test that empty list is returned when first port is invalid."""

    def mock_execute(cmd: str) -> str:
        return "Invalid port id"

    result = collect_all_interfaces(mock_execute)

    assert len(result) == 0


def test_parse_interface_output_gigabit_ethernet():
    """Test parsing GigabitEthernet interface with statistics."""
    output = """GigabitEthernet1 is up
  Hardware is Gigabit Ethernet
  Auto-duplex, Auto-speed, media type is Copper
  flow-control is off
     1059016090 packets input, 2902879441 bytes, 0 throttles
     Received 57937948 broadcasts (82930444 multicasts)
     0 runts, 0 giants, 0 throttles
     0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored
     82930444 multicast, 0 pause input
     0 input packets with dribble condition detected
     543385722 packets output, 2386478183 bytes, 0 underrun
     0 output errors, 0 collisions, 0 interface resets
     0 babbles, 0 late collision, 0 deferred
     0 PAUSE output"""

    result = parse_interface_output(output)

    assert result["name"] == "GigabitEthernet1"
    assert result["status"] == "up"
    assert result["hardware"] == "Gigabit Ethernet"
    assert result["duplex"] == "Auto"
    assert result["speed"] == "Auto"
    assert result["media_type"] == "Copper"
    assert result["flow_control"] == "off"

    stats = result["statistics"]
    assert stats["packets_input"] == 1059016090
    assert stats["bytes_input"] == 2902879441
    assert stats["throttles_input"] == 0
    assert stats["broadcasts"] == 57937948
    assert stats["multicasts"] == 82930444
    assert stats["runts"] == 0
    assert stats["giants"] == 0
    assert stats["input_errors"] == 0
    assert stats["crc_errors"] == 0
    assert stats["frame_errors"] == 0
    assert stats["overrun_errors"] == 0
    assert stats["ignored_errors"] == 0
    assert stats["multicast"] == 82930444
    assert stats["pause_input"] == 0
    assert stats["dribble_packets"] == 0
    assert stats["packets_output"] == 543385722
    assert stats["bytes_output"] == 2386478183
    assert stats["underrun"] == 0
    assert stats["output_errors"] == 0
    assert stats["collisions"] == 0
    assert stats["interface_resets"] == 0
    assert stats["babbles"] == 0
    assert stats["late_collisions"] == 0
    assert stats["deferred"] == 0
    assert stats["pause_output"] == 0


def test_parse_interface_output_lag_down():
    """Test parsing LAG interface that is down."""
    output = """show interface 32\r
LAG8 is down\r
  Hardware is Fast Ethernet\r
  Auto-duplex, Auto-speed, media type is Copper\r
  flow-control is off\r
     0 packets input, 0 bytes, 0 throttles\r
     Received 0 broadcasts (0 multicasts)\r
     0 runts, 0 giants, 0 throttles\r
     0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored\r
     0 multicast, 0 pause input\r
     0 input packets with dribble condition detected\r
     0 packets output, 0 bytes, 0 underrun\r
     0 output errors, 0 collisions, 0 interface resets\r
     0 babbles, 0 late collision, 0 deferred\r
     0 PAUSE output\r
GS1900# """

    result = parse_interface_output(output)

    assert result["name"] == "LAG8"
    assert result["status"] == "down"
    assert result["hardware"] == "Fast Ethernet"
    assert result["duplex"] == "Auto"
    assert result["speed"] == "Auto"
    assert result["media_type"] == "Copper"
    assert result["flow_control"] == "off"

    stats = result["statistics"]
    assert stats["packets_input"] == 0
    assert stats["bytes_input"] == 0
    assert stats["packets_output"] == 0
    assert stats["bytes_output"] == 0


def test_parse_interface_output_minimal():
    """Test parsing with minimal output (only name and status)."""
    output = "GigabitEthernet5 is down"

    result = parse_interface_output(output)

    assert result["name"] == "GigabitEthernet5"
    assert result["status"] == "down"
    assert "hardware" not in result
    assert "statistics" not in result


def test_parse_interface_output_empty():
    """Test parsing empty output."""
    result = parse_interface_output("")

    assert result == {}


def test_parse_interface_output_with_carriage_returns():
    """Test that parser handles \r\n line endings correctly."""
    output = "LAG5 is down\r\n  Hardware is Fast Ethernet\r\n  Auto-duplex, Auto-speed, media type is Copper\r\n"

    result = parse_interface_output(output)

    assert result["name"] == "LAG5"
    assert result["status"] == "down"
    assert result["hardware"] == "Fast Ethernet"
