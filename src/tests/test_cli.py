import sys
from io import StringIO
from unittest import TestCase
from unittest.mock import patch

from zyxel_cli import cli


class TestCli(TestCase):
    def test_main_no_command_exits(self):
        with patch.object(sys, "argv", ["zyxel-cli", "-H", "1.2.3.4"]):
            with self.assertRaises(SystemExit) as exc:
                cli.main()
        self.assertEqual(exc.exception.code, 1)

    def test_main_exec_uses_session(self):
        class FakeSession:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                return False

            def execute_command(self, *, command):
                return "RESULT: " + command

        out = StringIO()
        with patch.object(
            sys,
            "argv",
            ["zyxel-cli", "-H", "1.2.3.4", "-u", "admin", "-p", "pw", "exec", "show version"],
        ):
            with patch("zyxel_cli.commands.ZyxelSession", new=lambda *a, **k: FakeSession()):
                with patch("sys.stdout", new=out):
                    cli.main()

        output = out.getvalue()
        self.assertIn("RESULT: show version", output)
