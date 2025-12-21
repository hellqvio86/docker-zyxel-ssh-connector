import pytest


@pytest.fixture
def noop_sleep():
    """A no-op sleep helper for tests that want to avoid real delays."""
    return lambda s: None


def test_noop_sleep_fixture_available(noop_sleep):
    noop_sleep(0.01)
    assert True
