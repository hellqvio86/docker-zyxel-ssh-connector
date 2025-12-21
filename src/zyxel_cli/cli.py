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

}


def main() -> None:
    parser = create_parser()
    parser.epilog = """
Examples:
  %(prog)s -H 192.168.1.1 version
  %(prog)s -H switch.local -u admin -p pass123 config
  %(prog)s -H 192.168.1.1 exec "show ip interface"
        """
    
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
