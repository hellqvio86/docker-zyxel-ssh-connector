"""CLI interface for Zyxel switches"""

import sys

from .commands import create_parser, handle_args


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
    except Exception as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
