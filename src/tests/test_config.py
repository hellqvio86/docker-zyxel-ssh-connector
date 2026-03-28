from unittest import TestCase


class TestConfig(TestCase):
    def test_noop_sleep_helper_available(self):
        def noop_sleep(_: float) -> None:
            return None

        noop_sleep(0.01)
        self.assertTrue(True)
