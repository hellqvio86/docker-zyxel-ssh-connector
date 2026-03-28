import getpass
import sys
from unittest import TestCase
from unittest.mock import patch

from zyxel_cli.client import ZyxelSession
from zyxel_cli.config import resolve_password


class TestClientExtra(TestCase):
    def test_password_arg_wins_over_env(self):
        with patch.dict("os.environ", {"PASSWORD": "envpw"}, clear=False):
            pw = resolve_password(password="argpw", user="user", host="host")
        self.assertEqual(pw, "argpw")

    def test_password_env_used_when_no_arg(self):
        with patch.dict("os.environ", {"PASSWORD": "envpw"}, clear=False):
            pw = resolve_password(password=None, user="user", host="host")
        self.assertEqual(pw, "envpw")

    def test_password_prompt_used_when_no_arg_or_env(self):
        with patch.dict("os.environ", {}, clear=True):
            with patch.object(getpass, "getpass", return_value="promptpw"):
                pw = resolve_password(password=None, user="user", host="host")
        self.assertEqual(pw, "promptpw")

    def test_connect_raises_connectionerror_when_ssh_fails(self):
        class FakeSSH:
            def set_missing_host_key_policy(self, p):
                pass

            def connect(self, **k):
                raise Exception("boom")

        with patch("zyxel_cli.client.paramiko.SSHClient", new=lambda: FakeSSH()):
            s = ZyxelSession(host="h", user="u", password="p")
            with self.assertRaises(ConnectionError) as exc:
                s.connect()
        self.assertIn("Failed to connect to h", str(exc.exception))

    def test_context_manager_calls_connect_and_close(self):
        called = {"connect": False, "close": False}

        def fake_connect(self):
            called["connect"] = True

        def fake_close(self):
            called["close"] = True

        with patch("zyxel_cli.client.ZyxelSession.connect", new=fake_connect):
            with patch("zyxel_cli.client.ZyxelSession.close", new=fake_close):
                with ZyxelSession(host="h", user="u", password="p"):
                    self.assertTrue(called["connect"])
        self.assertTrue(called["close"])

    def test_execute_command_raises_when_not_connected(self):
        s = ZyxelSession(host="h", user="u", password="p")
        s.client = None
        with self.assertRaises(RuntimeError):
            s.execute_command(command="show version")

    def test_interactive_exits_on_eof(self):
        class FakeShell:
            def settimeout(self, t):
                pass

            def recv(self, n):
                return b""

            def send(self, data):
                pass

        class FakeClient:
            def invoke_shell(self):
                return FakeShell()

        s = ZyxelSession(host="h", user="u", password="p")
        s.client = FakeClient()  # type: ignore[assignment]

        class FakeTermios:
            TCSADRAIN = 0

            @staticmethod
            def tcgetattr(stdin):
                return "old"

            @staticmethod
            def tcsetattr(stdin, when, old):
                return None

        class FakeTty:
            @staticmethod
            def setraw(fd):
                return None

            @staticmethod
            def setcbreak(fd):
                return None

        class FakeStdin:
            def fileno(self):
                return 0

            def read(self, n=1):
                return ""

        fake_stdin = FakeStdin()

        class FakeSelect:
            @staticmethod
            def select(r, w, e):
                return ([fake_stdin], [], [])

        import zyxel_cli.client as client_mod2

        with patch.dict(sys.modules, {"termios": FakeTermios, "tty": FakeTty, "select": FakeSelect}):
            with patch.object(client_mod2.sys, "stdin", fake_stdin):
                s.interactive()
