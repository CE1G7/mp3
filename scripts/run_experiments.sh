#!/usr/bin/env bash
# Runs the section 5 experiments, one log set per phase, into results/.
# Legitimate camera interval is 10s and is NOT changed, so each phase needs
# enough wall time to collect a sample. DURATION dominates total runtime.
set -e
cd "$(dirname "$0")/.."

DURATION="${DURATION:-180}"
BASE="docker compose -f docker-compose.yml"
ATK="-f docker-compose.attack.yml"
MIT="-f docker-compose.mitigation.yml"
mkdir -p results

run_phase () {
  local name="$1"; shift
  echo "=== phase: $name (${DURATION}s) ==="
  $BASE "$@" down -v --remove-orphans >/dev/null 2>&1 || true
  rm -f logging/logs/all.jsonl logging/logs/alerts.jsonl
  $BASE "$@" up -d --build
  sleep "$DURATION"
  $BASE "$@" stop >/dev/null 2>&1
  cp logging/logs/all.jsonl    "results/${name}_all.jsonl"    2>/dev/null || echo "[]" > "results/${name}_all.jsonl"
  cp logging/logs/alerts.jsonl "results/${name}_alerts.jsonl" 2>/dev/null || : > "results/${name}_alerts.jsonl"
  echo "--- $name done: $(wc -l < results/${name}_all.jsonl) records"
}

# 1 baseline: legit cameras only
run_phase baseline

# 2 attack, no mitigation: one flooder
run_phase attack $ATK

# 3 attack, mitigation on
run_phase mitigated $ATK $MIT

# 4 botnet (3 flooders), mitigation on
DURATION="$DURATION" $BASE $ATK $MIT --profile botnet down -v --remove-orphans >/dev/null 2>&1 || true
rm -f logging/logs/all.jsonl logging/logs/alerts.jsonl
$BASE $ATK $MIT --profile botnet up -d --build
sleep "$DURATION"; $BASE $ATK $MIT --profile botnet stop >/dev/null 2>&1
cp logging/logs/all.jsonl results/botnet_all.jsonl 2>/dev/null || echo "[]" > results/botnet_all.jsonl
cp logging/logs/alerts.jsonl results/botnet_alerts.jsonl 2>/dev/null || : > results/botnet_alerts.jsonl
echo "--- botnet done: $(wc -l < results/botnet_all.jsonl) records"

# 5 rotating ID, mitigation on
rm -f logging/logs/all.jsonl logging/logs/alerts.jsonl
$BASE $ATK $MIT --profile rotate up -d --build
sleep "$DURATION"; $BASE $ATK $MIT --profile rotate stop >/dev/null 2>&1
cp logging/logs/all.jsonl results/rotate_all.jsonl 2>/dev/null || echo "[]" > results/rotate_all.jsonl
cp logging/logs/alerts.jsonl results/rotate_alerts.jsonl 2>/dev/null || : > results/rotate_alerts.jsonl
echo "--- rotate done"

# 6 spoofing cam_a, mitigation on
rm -f logging/logs/all.jsonl logging/logs/alerts.jsonl
$BASE $ATK $MIT --profile spoof up -d --build
sleep "$DURATION"; $BASE $ATK $MIT --profile spoof stop >/dev/null 2>&1
cp logging/logs/all.jsonl results/spoof_all.jsonl 2>/dev/null || echo "[]" > results/spoof_all.jsonl
cp logging/logs/alerts.jsonl results/spoof_alerts.jsonl 2>/dev/null || : > results/spoof_alerts.jsonl
echo "--- spoof done"

$BASE $ATK $MIT --profile botnet --profile rotate --profile spoof down -v --remove-orphans >/dev/null 2>&1 || true
echo "=== all phases complete. results/ populated. ==="
