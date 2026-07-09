#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EVENT_FILE="${1:-$ROOT/events/new-rtl-block.json}"

if [[ ! -f "$EVENT_FILE" ]]; then
  echo "Event file not found: $EVENT_FILE" >&2
  exit 1
fi

echo "Simulating incoming RTL request event:"
echo
cat "$EVENT_FILE"
echo
echo "Next step: send this payload to the local or cloud OpenHands automation entrypoint."

