#!/usr/bin/env bash
# screenshot.sh <editor-binary> <demo-project> <out-dir>: runs the editor in a virtual screen and takes screenshots.
# A fresh HOME makes the editor start with the defaults compiled into it (our theme and layout).
set -u
BIN="$(realpath "$1")"; DEMO="$(realpath "$2")"; OUT="$3"
mkdir -p "$OUT"
export HOME="$(mktemp -d)"
Xvfb :99 -screen 0 1600x900x24 >/dev/null 2>&1 &
XPID=$!
sleep 3
export DISPLAY=:99
COMMON=(--display-driver x11 --rendering-driver opengl3 --audio-driver Dummy)

"$BIN" "${COMMON[@]}" --project-manager --resolution 1280x720 --position 0,0 > "$OUT/project-manager.log" 2>&1 &
PID=$!
sleep 30
import -window root "$OUT/01-project-manager.png"
kill "$PID" 2>/dev/null; sleep 2

"$BIN" "${COMMON[@]}" --editor --path "$DEMO" --resolution 1600x900 --position 0,0 > "$OUT/editor.log" 2>&1 &
PID=$!
sleep 90
import -window root "$OUT/02-editor.png"
sleep 25
import -window root "$OUT/03-editor-later.png"
kill "$PID" 2>/dev/null
kill "$XPID" 2>/dev/null
ls -l "$OUT"
exit 0
