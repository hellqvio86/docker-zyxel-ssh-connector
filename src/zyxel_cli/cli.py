"""CLI interface for Zyxel switches"""

import argparse
import getpass
import sys

from .client import ZyxelSession
from .commands import create_parser, handle_args
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CLI tool for Zyxel GS1900 switches",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -H 192.168.1.1 version
  %(prog)s -H switch.local -u admin -p pass123 config
  %(prog)s -H 192.168.1.1 exec "show ip interface"
        """,
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

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        handle_args(args=args)
    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
