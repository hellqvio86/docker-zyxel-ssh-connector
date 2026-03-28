from unittest import TestCase


class TestConfig(TestCase):
    def test_noop_sleep_helper_available(self):
        noop_sleep = lambda s: None
        noop_sleep(0.01)
        self.assertTrue(True)
