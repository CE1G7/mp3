#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
NET="$(docker network ls --format '{{.Name}}' | grep mgmt | head -1)"
MSYS_NO_PATHCONV=1 docker run --rm --network "$NET" \
  -v "$(pwd)/scripts:/s" python:3.12-alpine \
  python /s/emit_traffic.py --mode "${1:-all}"
