"""Tests for port range expansion utility."""

import pytest
from zyxel_cli.parsing import expand_port_range


def test_expand_numeric_range():
    """Test expanding numeric port ranges."""
    result = expand_port_range("1-5")
    assert result == ["1", "2", "3", "4", "5"]


def test_expand_lag_range():
    """Test expanding LAG port ranges."""
    result = expand_port_range("lag1-4")
    assert result == ["lag1", "lag2", "lag3", "lag4"]


def test_expand_comma_separated():
    """Test expanding comma-separated ports."""
    result = expand_port_range("8,23")
    assert result == ["8", "23"]


def test_expand_single_port():
    """Test single port."""
    result = expand_port_range("23")
    assert result == ["23"]


def test_expand_empty_marker():
    """Test empty port marker '---'."""
    result = expand_port_range("---")
    assert result == []


def test_expand_empty_string():
    """Test empty string."""
    result = expand_port_range("")
    assert result == []


def test_expand_complex_range():
    """Test complex range with numeric and LAG ports."""
    result = expand_port_range("1-3,lag1-2")
    assert result == ["1", "2", "3", "lag1", "lag2"]


def test_expand_full_switch_range():
    """Test full 24-port switch with LAG range."""
    result = expand_port_range("1-24,lag1-8")
    expected = [str(i) for i in range(1, 25)] + [f"lag{i}" for i in range(1, 9)]
    assert result == expected


def test_expand_mixed_format():
    """Test mixed format with ranges and individual ports."""
    result = expand_port_range("1-3,5,7-9")
    assert result == ["1", "2", "3", "5", "7", "8", "9"]
