"""Utility functions for MAC address table parsing."""


def parse_mac_table_output(output: str) -> list[dict[str, str]]:
    """Parse MAC address table output into structured data.

    Args:
        output: Raw output from 'show mac address-table' command

    Returns:
        List of dictionaries containing MAC table entries with keys:
        - vid: VLAN ID
        - mac: MAC address
        - type: Entry type (Management, Dynamic, Static, etc.)
        - port: Port identifier
    """
    entries: list[dict[str, str]] = []
    lines = output.splitlines()

    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue

        # Skip header lines (contain "VID" or "MAC Address")
        if "VID" in line or "MAC Address" in line:
            continue

        # Skip separator lines (contain dashes)
        if line.strip().startswith("-"):
            continue

        # Skip "Total number of entries" line
        if "Total number" in line:
            continue

        # Skip prompts and commands
        if line.strip().startswith("GS1900") or line.strip().startswith("show "):
            continue

        # Handle --More-- prompt (may appear with backspace characters)
        if "--More--" in line:
            continue

        # Check if line contains pipe delimiters (actual data row)
        if "|" not in line:
            continue

        # Split by pipe and extract fields
        parts = [p.strip() for p in line.split("|")]

        # Valid data rows should have 4 parts: VID, MAC, Type, Port
        if len(parts) >= 4:
            vid = parts[0].strip()
            mac = parts[1].strip()
            entry_type = parts[2].strip()
            port = parts[3].strip()

            # Validate that we have actual data (not empty or just whitespace)
            if vid and mac and ":" in mac:
                entries.append({"vid": vid, "mac": mac, "type": entry_type, "port": port})

    return entries
