#!/usr/bin/env bash
# run-logged.sh <title> <command...>: runs a command, and if it fails publishes the relevant log lines
# as a GitHub error annotation (the full log is not retrievable from outside the runner).
title="$1"; shift
log="${RUNNER_TEMP:-/tmp}/$(echo "$title" | tr -c 'A-Za-z0-9' _).log"
set +e; "$@" > "$log" 2>&1; rc=$?; set -e
if [ $rc -ne 0 ]; then
  sel=$(grep -n -i -E "error:|FAILED|What went wrong|Caused by|Exception|\*\*\*|undefined reference|No such file|cannot find symbol|not found|incompatible|does not exist" "$log" | tail -n 25 | cut -c1-300)
  [ -z "$sel" ] && sel=$(tail -n 30 "$log" | cut -c1-300)
  msg=$(printf '%s' "$sel" | tail -c 3500 | sed 's/%/%25/g' | awk '{printf "%s%%0A", $0}')
  echo "::error title=$title failed::$msg"
  tail -n 40 "$log"
  exit $rc
fi
tail -n 6 "$log"
