#!/bin/bash
set -e

# Test script for debug logging
# Usage: ./scripts/test_debug_logging.sh <HOST> [USER] [PASSWORD]

HOST=$1
USER=${2:-admin}

# If password is not provided, prompt for it
if [ -z "$3" ]; then
    read -s -p "Password for $USER@$HOST: " PASS
    echo
else
    PASS=${3}
fi

if [ -z "$HOST" ]; then
    echo "Usage: $0 <HOST> [USER] [PASSWORD]"
    exit 1
fi

LOG_FILE="zyxel_ssh_debug.log"
# Cleanup previous log
rm -f "$LOG_FILE"

echo "Running read-only commands with --debug..."

# Define commands to test
COMMANDS=("version" "config" "interfaces" "vlans" "mac-table")

for cmd in "${COMMANDS[@]}"; do
    echo "Testing command: $cmd"
    # Run command with --debug
    if [ -n "$PASS" ]; then
        uv run zyxel-cli -H "$HOST" -u "$USER" -p "$PASS" --debug "$cmd"
    else
        # Allow password prompt or SSH key if configured (but prompt breaks automation)
        echo "Warning: No password provided, this might hang if prompt appears."
        uv run zyxel-cli -H "$HOST" -u "$USER" --debug "$cmd"
    fi
done

echo "Checking log file..."
if [ -f "$LOG_FILE" ]; then
    echo "✅ Log file created: $LOG_FILE"
    echo "Log content sample:"
    head -n 2 "$LOG_FILE"
    
    # Verify JSON format of first line
    first_line=$(head -n 1 "$LOG_FILE")
    if echo "$first_line" | python3 -c "import sys, json; json.load(sys.stdin)"; then
        echo "✅ Log format is valid JSON"
    else
        echo "❌ Log format is NOT valid JSON"
        exit 1
    fi
else
    echo "❌ Log file NOT created"
    exit 1
fi

echo "✅ All logging tests passed!"
