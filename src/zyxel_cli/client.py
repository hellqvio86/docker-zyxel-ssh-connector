"""SSH client for Zyxel switches"""

import re
import sys
import time
from typing import Any, Optional

import paramiko


class ZyxelSession:
    """SSH session handler for Zyxel switches"""

    def __init__(self, host: str, user: str, *, password: Optional[str] = None, port: int = 22):
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.client: Optional[paramiko.SSHClient] = None

    def connect(self) -> None:
        """Establish SSH connection"""
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            self.client.connect(
                hostname=self.host,
                port=self.port,
                username=self.user,
                password=self.password,
                look_for_keys=False,
                allow_agent=False,
                timeout=10,
            )
        except Exception as e:
            raise ConnectionError(f"Failed to connect to {self.host}: {e}")

    def execute_command(self, *, command: str) -> str:
        """Execute a command on the Zyxel switch"""
        if not self.client:
            raise RuntimeError("Not connected")

        # Open an interactive shell
        shell = self.client.invoke_shell()
        time.sleep(0.5)

        # Clear initial output
        if shell.recv_ready():
            shell.recv(4096)

        # Send newline to get prompt
        shell.send(b"\n")
        time.sleep(0.3)

        # Clear prompt
        if shell.recv_ready():
            shell.recv(4096)

        # Send the actual command (send bytes to satisfy stubs)
        shell.send(f"{command}\n".encode("utf-8"))
        time.sleep(0.5)

        # Collect output
        # Collect output
        output = ""
        idle_count = 0
        max_idle = 20  # 2 seconds timeout (20 * 0.1)

        while idle_count < max_idle:
            if shell.recv_ready():
                chunk = shell.recv(4096).decode("utf-8", errors="ignore")
                output += chunk
                idle_count = 0  # Reset idle counter when data received

                if "--More--" in chunk:
                    shell.send(b" ")
            else:
                time.sleep(0.1)
                idle_count += 1

        # Send exit
        shell.send(b"exit\n")
        shell.close()

        return self._clean_output(output)

    def interactive(self) -> None:
        """Start an interactive SSH session"""
        if not self.client:
            raise RuntimeError("Not connected")

        print(f"Connected to {self.host}. Press Ctrl+D to exit.\n")

        shell = self.client.invoke_shell()

        import select
        import termios
        import tty

        oldtty = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())
            tty.setcbreak(sys.stdin.fileno())
            shell.settimeout(0.0)

            while True:
                r, w, e = select.select([shell, sys.stdin], [], [])
                if shell in r:
                    try:
                        recv_bytes = shell.recv(1024)
                        if len(recv_bytes) == 0:
                            break
                        sys.stdout.write(recv_bytes.decode("utf-8", errors="ignore"))
                        sys.stdout.flush()
                    except:
                        pass

                if sys.stdin in r:
                    input_char = sys.stdin.read(1)
                    if len(input_char) == 0:
                        break
                    shell.send(input_char.encode("utf-8"))
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)

    def close(self) -> None:
        """Close the SSH connection"""
        if self.client:
            self.client.close()

    @staticmethod
    def _clean_output(output: str) -> str:
        """Clean ANSI escape codes and prompts from output"""
        # Remove ANSI escape sequences
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        cleaned = ansi_escape.sub("", output)

        # Remove prompts and empty lines
        lines = []
        for line in cleaned.split("\n"):
            stripped = line.strip()
            if (
                stripped
                and not stripped.startswith("Switch>")
                and not stripped.startswith("Switch#")
            ):
                lines.append(line)

        return "\n".join(lines)

    def __enter__(self) -> "ZyxelSession":
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        """Context manager exit"""
        self.close()
