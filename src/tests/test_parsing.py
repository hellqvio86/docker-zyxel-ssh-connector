from zyxel_cli import parsing


def test_parse_version():
    output = "Boot Version     : V2.00 | 07/08/2015\nFirmware Version : V2.50(AAHK.0) | 10/21/2019"
    data = parsing.parse_version(output)
    assert data["Boot Version"] == "V2.00"
    assert data["Firmware Version"] == "V2.50(AAHK.0)"


def test_parse_vlan():
    output = """
  VID  |     VLAN Name    |        Untagged Ports        |        Tagged Ports          |  Type   
-------+------------------+------------------------------+------------------------------+---------
     1 |          default |                  1-24,lag1-8 |                          --- | Default 
     2 |            ALARM |                          --- |                           23 | Static 
    """
    vlans = parsing.parse_vlan(output)
    assert len(vlans) == 2
    assert vlans[0]["vid"] == "1"
    assert vlans[0]["name"] == "default"
    assert vlans[0]["untagged_ports"] == "1-24,lag1-8"
    assert vlans[0]["tagged_ports"] == "---"
    assert vlans[0]["type"] == "Default"

    assert vlans[1]["vid"] == "2"
    assert vlans[1]["name"] == "ALARM"


def test_parse_mac_table():
    output = """
     1  00:11:22:33:44:55  dynamic  1
    10  AA:BB:CC:DD:EE:FF  static   2
    invalid line
    """
    entries = parsing.parse_mac_table(output)
    assert len(entries) == 2
    assert entries[0]["vlan"] == "1"
    assert entries[0]["mac"] == "00:11:22:33:44:55"

    assert entries[1]["vlan"] == "10"
    assert entries[1]["mac"] == "AA:BB:CC:DD:EE:FF"


def test_parse_interfaces_error():
    output = "Invalid port id"
    data = parsing.parse_interfaces(output)
    assert len(data) == 1
    assert data[0]["error"] == "Invalid port id"


def test_parse_config():
    output = "hostname Switch\ninterface vlan 1\n ip address 1.2.3.4"
    data = parsing.parse_config(output)
    assert "lines" in data
    assert len(data["lines"]) == 3
