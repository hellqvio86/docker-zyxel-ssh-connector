"""Command handling separated from CLI entrypoint for easier testing."""

import argparse
import logging
from typing import Optional

from .client import ZyxelSession
from .config import resolve_password
from .interface_utils import collect_all_interfaces, parse_interface_output

LOGGER = logging.getLogger("zyxel_cli")

# Command mapping (interfaces handled separately with iteration logic)
COMMANDS: dict[str, str] = {
    "version": "show version",
    "config": "show running-config",
    "vlans": "show vlan",
    "mac-table": "show mac address-table",
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
    parser.add_argument("--debug", action="store_true", help="Enable JSON debug logging to file")
    parser.add_argument("--output-json", action="store_true", help="Output results as JSON")

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    subparsers.add_parser("version", help="Show switch version")
    subparsers.add_parser("config", help="Show running configuration")
    subparsers.add_parser("interfaces", help="Show interface status")
    subparsers.add_parser("vlans", help="Show VLAN configuration")
    subparsers.add_parser("mac-table", help="Show MAC address table")

    exec_parser = subparsers.add_parser("exec", help="Execute custom command")
    exec_parser.add_argument("exec_command", help="Command to execute")

    subparsers.add_parser("interactive", help="Interactive shell")

    return parser


def handle_args(*, args: argparse.Namespace) -> Optional[str]:
    """Execute the requested action described by parsed `args`.

    Returns output string for non-interactive commands, or None for interactive.
    """
    import json

    from .logging_config import setup_logging
    from .parsing import parse_output

    setup_logging(debug=args.debug)

    password = resolve_password(password=args.password, user=args.user, host=args.host)

    cmd_str = args.command
    if args.command == "exec":
        cmd_str = f"exec: {args.exec_command}"

    LOGGER.debug(f"Connecting to {args.host}", extra={"host": args.host, "command": cmd_str})

    with ZyxelSession(host=args.host, user=args.user, password=password, port=args.port) as session:
        if args.command == "interactive":
            session.interactive()
            return None
        elif args.command == "exec":
            output = session.execute_command(command=args.exec_command)
            # Log output (escaping newlines could be good but raw string in JSON is handled by json.dumps)
            LOGGER.debug(
                "Command result",
                extra={"host": args.host, "command": args.exec_command, "output": output},
            )

            if args.output_json:
                result = parse_output(args.exec_command, output)

                LOGGER.debug(
                    "Parsed json result",
                    extra={"host": args.host, "command": args.exec_command, "output": result},
                )

                print(json.dumps(result, indent=2))
            else:
                print(output)
            return output
        elif args.command == "interfaces":
            # Special handling: iterate through all port IDs
            LOGGER.debug(
                "Collecting all interfaces",
                extra={"host": args.host, "command": "interfaces"},
            )

            interfaces = collect_all_interfaces(lambda cmd: session.execute_command(command=cmd))

            # Combine all outputs
            output_parts = []
            for port_id, port_output in interfaces:
                output_parts.append(f"=== Interface {port_id} ===")
                output_parts.append(port_output)
                output_parts.append("")  # Empty line between interfaces

            output = "\n".join(output_parts)

            LOGGER.debug(
                "Command result",
                extra={"host": args.host, "command": "interfaces", "output": output},
            )

            if args.output_json:
                # For JSON output, create a structured format with parsed data
                result = {
                    "interfaces": [
                        {
                            "port_id": port_id,
                            "parsed": parse_interface_output(port_output),
                            "raw_output": port_output,
                        }
                        for port_id, port_output in interfaces
                    ]
                }

                LOGGER.debug(
                    "Parsed json result",
                    extra={"host": args.host, "command": "interfaces", "output": result},
                )
                print(json.dumps(result, indent=2))
            else:
                print(output)
            return output
        else:
            cmd = COMMANDS.get(args.command)
            if cmd:
                output = session.execute_command(command=cmd)
                LOGGER.debug(
                    "Command result", extra={"host": args.host, "command": cmd, "output": output}
                )

                if args.output_json:
                    result = parse_output(cmd, output)

                    LOGGER.debug(
                        "Parsed json result",
                        extra={"host": args.host, "command": args.command, "output": result},
                    )
                    print(json.dumps(result, indent=2))
                else:
                    print(output)
                return output

    return None
