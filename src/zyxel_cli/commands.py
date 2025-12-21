"""Command handling separated from CLI entrypoint for easier testing."""
import argparse
from typing import Optional

from .client import ZyxelSession
from .config import resolve_password

# Command mapping
COMMANDS: dict[str, str] = {
    "version": "show version",
    "config": "show running-config",
    "interfaces": "show interface status",
    "vlans": "show vlan",
    "mac-table": "show mac address-table",
    "system": "show system-info",
}


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CLI tool for Zyxel GS1900 switches",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("-H", "--host", required=True, help="Switch hostname or IP")
    parser.add_argument("-u", "--user", default="admin", help="SSH username (default: admin)")
    parser.add_argument("-p", "--password", help="SSH password (will prompt if not provided)")
    parser.add_argument("--port", type=int, default=22, help="SSH port (default: 22)")

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    subparsers.add_parser("version", help="Show switch version")
    subparsers.add_parser("config", help="Show running configuration")
    subparsers.add_parser("interfaces", help="Show interface status")
    subparsers.add_parser("vlans", help="Show VLAN configuration")
    subparsers.add_parser("mac-table", help="Show MAC address table")
    subparsers.add_parser("system", help="Show system information")

    exec_parser = subparsers.add_parser("exec", help="Execute custom command")
    exec_parser.add_argument("exec_command", help="Command to execute")

    subparsers.add_parser("interactive", help="Interactive shell")

    return parser


def handle_args(*, args: argparse.Namespace) -> Optional[str]:
    """Execute the requested action described by parsed `args`.

    Returns output string for non-interactive commands, or None for interactive.
    """
    password = resolve_password(password=args.password, user=args.user, host=args.host)

    with ZyxelSession(host=args.host, user=args.user, password=password, port=args.port) as session:
        if args.command == "interactive":
            session.interactive()
            return None
        elif args.command == "exec":
            output = session.execute_command(command=args.exec_command)
            print(output)
            return output
        else:
            cmd = COMMANDS.get(args.command)
            if cmd:
                output = session.execute_command(command=cmd)
                print(output)
                return output

    return None
