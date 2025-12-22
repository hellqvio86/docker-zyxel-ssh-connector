"""Tests for mac_table_utils module."""

from zyxel_cli.mac_table_utils import parse_mac_table_output


def test_parse_mac_table_output_with_entries():
    """Test parsing MAC table with real data from debug log."""
    output = """show mac address-table\r
 VID  |    MAC Address    |       Type        |   Ports        \r
------+-------------------+-------------------+----------------\r
    1 | AA:BB:CC:11:22:33 |    Management     | CPU\r
    1 | 11:22:33:44:55:66 |      Dynamic      | 1 \r
    1 | 22:33:44:55:66:77 |      Dynamic      | 1 \r
    1 | 33:44:55:66:77:88 |      Dynamic      | 1 \r
    1 | 44:55:66:77:88:99 |      Dynamic      | 1 \r
    1 | 55:66:77:88:99:AA |      Dynamic      | 23 \r
    1 | 66:77:88:99:AA:BB |      Dynamic      | 3 \r
    1 | 77:88:99:AA:BB:CC |      Dynamic      | 3 \r
    1 | 88:99:AA:BB:CC:DD |      Dynamic      | 3 \r
Total number of entries: 9\r
GS1900# """

    result = parse_mac_table_output(output)

    assert len(result) == 9
    assert result[0] == {
        "vid": "1",
        "mac": "AA:BB:CC:11:22:33",
        "type": "Management",
        "port": "CPU",
    }
    assert result[1] == {"vid": "1", "mac": "11:22:33:44:55:66", "type": "Dynamic", "port": "1"}
    assert result[8] == {"vid": "1", "mac": "88:99:AA:BB:CC:DD", "type": "Dynamic", "port": "3"}


def test_parse_mac_table_output_with_more_prompt():
    """Test parsing MAC table with --More-- prompt."""
    output = """show mac address-table\r
 VID  |    MAC Address    |       Type        |   Ports        \r
------+-------------------+-------------------+----------------\r
    1 | AA:BB:CC:11:22:33 |    Management     | CPU\r
    1 | 11:22:33:44:55:66 |      Dynamic      | 1 \r
--More--\b\r
    1 | 99:AA:BB:CC:DD:EE |      Dynamic      | 1 \r
    1 | AA:BB:CC:DD:EE:FF |      Dynamic      | 1 \r
    4 | BB:CC:DD:EE:FF:00 |      Dynamic      | 1 \r
Total number of entries: 5\r
GS1900# """

    result = parse_mac_table_output(output)

    assert len(result) == 5
    assert result[0] == {
        "vid": "1",
        "mac": "AA:BB:CC:11:22:33",
        "type": "Management",
        "port": "CPU",
    }
    assert result[4] == {
        "vid": "4",
        "mac": "BB:CC:DD:EE:FF:00",
        "type": "Dynamic",
        "port": "1",
    }


def test_parse_mac_table_output_multiple_vlans():
    """Test parsing MAC table with entries from multiple VLANs."""
    output = """ VID  |    MAC Address    |       Type        |   Ports        
------+-------------------+-------------------+----------------
    1 | AA:BB:CC:11:22:33 |    Management     | CPU
    1 | 11:22:33:44:55:66 |      Dynamic      | 1 
    4 | 22:33:44:55:66:77 |      Dynamic      | 1 
    7 | 33:44:55:66:77:88 |      Static       | 5 
Total number of entries: 4"""

    result = parse_mac_table_output(output)

    assert len(result) == 4
    assert result[0]["vid"] == "1"
    assert result[2]["vid"] == "4"
    assert result[3]["vid"] == "7"
    assert result[3]["type"] == "Static"


def test_parse_mac_table_output_empty():
    """Test parsing empty MAC table."""
    output = """ VID  |    MAC Address    |       Type        |   Ports        
------+-------------------+-------------------+----------------
Total number of entries: 0"""

    result = parse_mac_table_output(output)

    assert len(result) == 0


def test_parse_mac_table_output_header_only():
    """Test parsing with only headers (no data)."""
    output = """ VID  |    MAC Address    |       Type        |   Ports        
------+-------------------+-------------------+----------------"""

    result = parse_mac_table_output(output)

    assert len(result) == 0


def test_parse_mac_table_output_with_trailing_spaces():
    """Test that parser handles trailing spaces correctly."""
    output = """    1 | AA:BB:CC:11:22:33 |    Management     | CPU    
    1 | 11:22:33:44:55:66 |      Dynamic      | 1     """

    result = parse_mac_table_output(output)

    assert len(result) == 2
    assert result[0]["port"] == "CPU"
    assert result[1]["port"] == "1"


def test_parse_mac_table_output_real_debug_log_data():
    """Test with exact data structure from the user's debug log."""
    output = """show mac address-table\r
 VID  |    MAC Address    |       Type        |   Ports        \r
------+-------------------+-------------------+----------------\r
    1 | AA:BB:CC:11:22:33 |    Management     | CPU\r
    1 | 11:22:33:44:55:01 |      Dynamic      | 1 \r
    1 | 11:22:33:44:55:02 |      Dynamic      | 1 \r
    1 | 11:22:33:44:55:03 |      Dynamic      | 1 \r
    1 | 11:22:33:44:55:04 |      Dynamic      | 1 \r
    1 | 11:22:33:44:55:05 |      Dynamic      | 23 \r
    1 | 11:22:33:44:55:06 |      Dynamic      | 3 \r
    1 | 11:22:33:44:55:07 |      Dynamic      | 3 \r
    1 | 11:22:33:44:55:08 |      Dynamic      | 3 \r
    1 | 11:22:33:44:55:09 |      Dynamic      | 1 \r
    1 | 11:22:33:44:55:0A |      Dynamic      | 1 \r
    1 | 11:22:33:44:55:0B |      Dynamic      | 1 \r
    1 | 11:22:33:44:55:0C |      Dynamic      | 3 \r
    1 | 11:22:33:44:55:0D |      Dynamic      | 1 \r
    1 | 11:22:33:44:55:0E |      Dynamic      | 1 \r
    1 | 11:22:33:44:55:0F |      Dynamic      | 1 \r
    1 | 11:22:33:44:55:10 |      Dynamic      | 1 \r
    1 | 11:22:33:44:55:11 |      Dynamic      | 1 \r
    1 | 11:22:33:44:55:12 |      Dynamic      | 1 \r
    1 | 11:22:33:44:55:13 |      Dynamic      | 1 \r
    1 | 11:22:33:44:55:14 |      Dynamic      | 6 \r
    1 | 11:22:33:44:55:15 |      Dynamic      | 1 \r
--More--\b\r
    1 | 11:22:33:44:55:16 |      Dynamic      | 1 \r
    1 | 11:22:33:44:55:17 |      Dynamic      | 1 \r
    1 | 11:22:33:44:55:18 |      Dynamic      | 1 \r
    4 | 22:33:44:55:66:77 |      Dynamic      | 1 \r
Total number of entries: 26\r
GS1900# """

    result = parse_mac_table_output(output)

    assert len(result) == 26
    # Check first entry
    assert result[0] == {
        "vid": "1",
        "mac": "AA:BB:CC:11:22:33",
        "type": "Management",
        "port": "CPU",
    }
    # Check last entry (different VLAN)
    assert result[25] == {
        "vid": "4",
        "mac": "22:33:44:55:66:77",
        "type": "Dynamic",
        "port": "1",
    }
    # Check an entry after --More-- prompt
    assert result[22]["mac"] == "11:22:33:44:55:16"
