from typing import Any, Dict, List, Union


def expand_port_range(port_str: str) -> List[str]:
    """
    Expand port range string into individual ports.

    Examples:
        "1-24,lag1-8" -> ["1", "2", ..., "24", "lag1", "lag2", ..., "lag8"]
        "8,23" -> ["8", "23"]
        "23" -> ["23"]
        "---" -> []
    """
    if not port_str or port_str.strip() == "---":
        return []

    ports = []
    segments = port_str.split(",")

    for segment in segments:
        segment = segment.strip()
        if not segment or segment == "---":
            continue

        # Check if it's a range (contains hyphen)
        if "-" in segment:
            # Handle LAG ranges (e.g., "lag1-8")
            if segment.lower().startswith("lag"):
                # Extract the numeric parts
                parts = segment.split("-")
                prefix = parts[0].rstrip("0123456789")  # "lag"
                start_num = int(parts[0][len(prefix) :])  # Extract number from "lag1"
                end_num = int(parts[1])

                for i in range(start_num, end_num + 1):
                    ports.append(f"{prefix}{i}")
            else:
                # Handle numeric ranges (e.g., "1-24")
                start, end = segment.split("-")
                for i in range(int(start), int(end) + 1):
                    ports.append(str(i))
        else:
            # Single port
            ports.append(segment)

    return ports


def parse_version(output: str) -> Dict[str, str]:
    """Parse 'show version' output."""
    data = {}
    for line in output.splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            # Remove pipes if present (e.g. V2.00 | 07/08/2015)
            val = val.split("|")[0].strip()
            data[key.strip()] = val
    return data


def parse_vlan(output: str) -> List[Dict[str, Union[str, List[str]]]]:
    """Parse 'show vlan' output."""
    vlans = []
    lines = output.splitlines()
    header_found = False

    for line in lines:
        if "VID" in line and "VLAN Name" in line:
            header_found = True
            continue
        if not header_found:
            continue
        if line.startswith("-") or not line.strip():
            continue

        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 2:
            vlan: Dict[str, Union[str, List[str]]] = {
                "vid": parts[0],
                "name": parts[1],
            }
            if len(parts) > 2:
                vlan["untagged_ports"] = expand_port_range(parts[2])
            if len(parts) > 3:
                vlan["tagged_ports"] = expand_port_range(parts[3])
            if len(parts) > 4:
                vlan["type"] = parts[4]
            vlans.append(vlan)
    return vlans


def parse_interfaces(output: str) -> List[Dict[str, str]]:
    """Parse 'show interface status' output (generic table parser)."""
    # Without strict schema, we'll try to parse generic tables or return raw lines
    # If it's the "Invalid port id" error or similar, return as error field
    if "Invalid" in output or "Error" in output:
        return [{"error": output.strip()}]

    # Attempt simple whitespace/column parsing if it looks like a table
    lines = output.splitlines()
    interfaces = []
    # TODO: Refine with actual output samples. For now returning line info.
    for line in lines:
        if line.strip():
            interfaces.append({"raw": line.strip()})
    return interfaces


def parse_mac_table(output: str) -> List[Dict[str, str]]:
    """Parse 'show mac address-table' output."""
    from .mac_table_utils import parse_mac_table_output

    return parse_mac_table_output(output)


def parse_config(output: str) -> Dict[str, Any]:
    """Parse 'show running-config' output."""
    # Running config is huge, returning as lines or raw is usually safest unless specific parsing needed
    return {"lines": output.splitlines()}


def parse_output(command: str, output: str) -> Any:
    """Dispatch output to appropriate parser."""
    command = command.strip()

    if command == "show version":
        return parse_version(output)
    elif command == "show vlan":
        return parse_vlan(output)
    elif command == "show interface status":
        return parse_interfaces(output)
    elif command == "show mac address-table":
        return parse_mac_table(output)
    elif command == "show running-config":
        return parse_config(output)

    # helper for mapped commands (aliases)
    if command == "version":
        return parse_version(output)
    if command == "vlans":
        return parse_vlan(output)
    if command == "interfaces":
        return parse_interfaces(output)
    if command == "config":
        return parse_config(output)

    # Default fallback
    return {"output": output}
