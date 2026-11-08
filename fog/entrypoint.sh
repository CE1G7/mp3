#!/bin/sh
IFACE=$(ip -o -4 addr show | awk '/10\.20\.0\./ {print $2}')
tc qdisc add dev "$IFACE" root netem delay 50ms 5ms
exec "$@"
