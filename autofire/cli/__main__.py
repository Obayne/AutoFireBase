"""
AutoFire CLI - Main entry point for command-line tools.
"""

import sys

from autofire.cli.device import main as device_main


def main() -> None:
    """Main CLI entry point that dispatches to subcommands."""
    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h"):
        print("AutoFire CLI")
        print("Usage: autofire-cli <command> [options]")
        print()
        print("Available commands:")
        print("  device    Device catalog management")
        print("  system    System management (coming soon)")
        print()
        print("For help on a specific command, run: autofire-cli <command> --help")
        sys.exit(0)

    command = sys.argv[1].lower()

    # Remove the command from argv so subcommands see their own args
    sys.argv = [sys.argv[0]] + sys.argv[2:]

    if command in ("device", "devices", "dev"):
        device_main()
    elif command in ("system", "sys"):
        print("System management CLI coming soon!")
        sys.exit(1)
    else:
        print(f"Unknown command: {command}")
        print("Available commands: device, system")
        sys.exit(1)


if __name__ == "__main__":
    main()
