"""Utility functions for interface operations."""

import re
from collections.abc import Callable
from typing import Any


def is_invalid_port_response(output: str) -> bool:
    """Check if the output indicates an invalid port ID.

    Args:
        output: The command output to check

    Returns:
        True if the output contains "Invalid port id", False otherwise
    """
    return "Invalid port id" in output


def parse_interface_output(output: str) -> dict[str, Any]:
    """Parse individual interface output into structured data.

    Args:
        output: Raw output from 'show interface <id>' command

    Returns:
        Dictionary containing parsed interface information including:
        - name: Interface name (e.g., "GigabitEthernet1", "LAG8")
        - status: "up" or "down"
        - hardware: Hardware type
        - duplex: Duplex setting
        - speed: Speed setting
        - media_type: Media type (e.g., "Copper")
        - flow_control: Flow control status
        - statistics: Dict of packet statistics
    """
    result: dict[str, Any] = {}

    # Extract interface name and status from first line
    # Example: "GigabitEthernet1 is up" or "LAG8 is down"
    first_line_match = re.search(r"^(\S+)\s+is\s+(up|down)", output, re.MULTILINE)
    if first_line_match:
        result["name"] = first_line_match.group(1)
        result["status"] = first_line_match.group(2)

    # Extract hardware type
    # Example: "  Hardware is Gigabit Ethernet"
    hardware_match = re.search(r"Hardware is (.+?)$", output, re.MULTILINE)
    if hardware_match:
        result["hardware"] = hardware_match.group(1).strip()

    # Extract duplex, speed, and media type
    # Example: "  Auto-duplex, Auto-speed, media type is Copper"
    config_match = re.search(r"([\w-]+)-duplex,\s*([\w-]+)-speed,\s*media type is (\w+)", output)
    if config_match:
        result["duplex"] = config_match.group(1)
        result["speed"] = config_match.group(2)
        result["media_type"] = config_match.group(3)

    # Extract flow control
    # Example: "  flow-control is off"
    flow_match = re.search(r"flow-control is (\w+)", output)
    if flow_match:
        result["flow_control"] = flow_match.group(1)

    # Extract statistics
    stats: dict[str, int] = {}

    # Input statistics
    # Example: "     1059016090 packets input, 2902879441 bytes, 0 throttles"
    input_match = re.search(r"(\d+) packets input, (\d+) bytes, (\d+) throttles", output)
    if input_match:
        stats["packets_input"] = int(input_match.group(1))
        stats["bytes_input"] = int(input_match.group(2))
        stats["throttles_input"] = int(input_match.group(3))

    # Broadcasts and multicasts
    # Example: "     Received 57937948 broadcasts (82930444 multicasts)"
    bcast_match = re.search(r"Received (\d+) broadcasts \((\d+) multicasts\)", output)
    if bcast_match:
        stats["broadcasts"] = int(bcast_match.group(1))
        stats["multicasts"] = int(bcast_match.group(2))

    # Input errors
    # Example: "     0 runts, 0 giants, 0 throttles"
    runts_match = re.search(r"(\d+) runts, (\d+) giants", output)
    if runts_match:
        stats["runts"] = int(runts_match.group(1))
        stats["giants"] = int(runts_match.group(2))

    # More input errors
    # Example: "     0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored"
    errors_match = re.search(
        r"(\d+) input errors, (\d+) CRC, (\d+) frame, (\d+) overrun, (\d+) ignored",
        output,
    )
    if errors_match:
        stats["input_errors"] = int(errors_match.group(1))
        stats["crc_errors"] = int(errors_match.group(2))
        stats["frame_errors"] = int(errors_match.group(3))
        stats["overrun_errors"] = int(errors_match.group(4))
        stats["ignored_errors"] = int(errors_match.group(5))

    # Multicast and pause input
    # Example: "     82930444 multicast, 0 pause input"
    multicast_match = re.search(r"(\d+) multicast, (\d+) pause input", output)
    if multicast_match:
        stats["multicast"] = int(multicast_match.group(1))
        stats["pause_input"] = int(multicast_match.group(2))

    # Dribble condition
    # Example: "     0 input packets with dribble condition detected"
    dribble_match = re.search(r"(\d+) input packets with dribble condition", output)
    if dribble_match:
        stats["dribble_packets"] = int(dribble_match.group(1))

    # Output statistics
    # Example: "     543385722 packets output, 2386478183 bytes, 0 underrun"
    output_match = re.search(r"(\d+) packets output, (\d+) bytes, (\d+) underrun", output)
    if output_match:
        stats["packets_output"] = int(output_match.group(1))
        stats["bytes_output"] = int(output_match.group(2))
        stats["underrun"] = int(output_match.group(3))

    # Output errors
    # Example: "     0 output errors, 0 collisions, 0 interface resets"
    output_errors_match = re.search(
        r"(\d+) output errors, (\d+) collisions, (\d+) interface resets", output
    )
    if output_errors_match:
        stats["output_errors"] = int(output_errors_match.group(1))
        stats["collisions"] = int(output_errors_match.group(2))
        stats["interface_resets"] = int(output_errors_match.group(3))

    # More output errors
    # Example: "     0 babbles, 0 late collision, 0 deferred"
    babbles_match = re.search(r"(\d+) babbles, (\d+) late collision, (\d+) deferred", output)
    if babbles_match:
        stats["babbles"] = int(babbles_match.group(1))
        stats["late_collisions"] = int(babbles_match.group(2))
        stats["deferred"] = int(babbles_match.group(3))

    # Pause output
    # Example: "     0 PAUSE output"
    pause_output_match = re.search(r"(\d+) PAUSE output", output)
    if pause_output_match:
        stats["pause_output"] = int(pause_output_match.group(1))

    if stats:
        result["statistics"] = stats

    return result


def collect_all_interfaces(execute_fn: Callable[[str], str]) -> list[tuple[int, str]]:
    """Collect all valid interfaces by iterating through port IDs.

    Starts at port ID 1 and continues incrementing until receiving
    "Invalid port id" response.

    Args:
        execute_fn: Function that executes a command and returns output.
                   Should accept a command string and return the output.

    Returns:
        List of tuples containing (port_id, output) for each valid interface
    """
    interfaces: list[tuple[int, str]] = []
    port_id = 1

    while True:
        command = f"show interface {port_id}"
        output = execute_fn(command)

        if is_invalid_port_response(output):
            break

        interfaces.append((port_id, output))
        port_id += 1

    return interfaces
