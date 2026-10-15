#!/usr/bin/env bash
# Runs inside the emulator: installs the APK, drives the launcher a little, records a video and
# checks that the bundled Fabric/Meteor files were placed in the game directory.
set -u
APK="$1"; OUT="${OUT:-emulator-out}"; PKG=net.kdt.pojavlaunch.debug
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$OUT"
shot() { adb exec-out screencap -p > "$OUT/$1.png" 2>/dev/null; echo "shot $1 $(stat -c %s "$OUT/$1.png") bytes"; }
ui() { python3 "$HERE/ui.py" "$@" >> "$OUT/ui-log.txt" 2>&1; tail -n 3 "$OUT/ui-log.txt"; }

adb wait-for-device
{ echo "android $(adb shell getprop ro.build.version.release | tr -d '\r') sdk $(adb shell getprop ro.build.version.sdk | tr -d '\r')"
  echo "abis $(adb shell getprop ro.product.cpu.abilist | tr -d '\r')"; } | tee "$OUT/device.txt"
adb install -r "$APK" 2>&1 | tee "$OUT/install.txt"
adb logcat -c

# 150 s of video (the recorder's limit is 180 s)
( adb shell screenrecord --time-limit 150 --bit-rate 3000000 --size 720x1280 /sdcard/rec.mp4 >/dev/null 2>&1 & )
sleep 2
adb shell monkey -p "$PKG" -c android.intent.category.LAUNCHER 1 2>&1 | tee "$OUT/start.txt"
sleep 35; shot 01-start; echo "== screen 1 (main)" >> "$OUT/ui-log.txt"; ui texts
running() { adb shell "ps -A | grep -c $PKG" | tr -d '\r'; }
echo "processes after start: $(running)" | tee "$OUT/alive.txt"

# profile editor (shows the bundled Meteor profile), then back to the main screen (one BACK only)
ui tap-id edit_profile_button; sleep 4; shot 02-profile-editor; echo "== screen 2 (profile editor)" >> "$OUT/ui-log.txt"; ui texts
adb shell input keyevent KEYCODE_BACK; sleep 3

# account menu
ui tap-id account_spinner; sleep 3; shot 03-accounts; echo "== screen 3 (accounts)" >> "$OUT/ui-log.txt"; ui texts
ui tap-text "add account"; sleep 3; shot 04-add-account; echo "== screen 4 (add account)" >> "$OUT/ui-log.txt"; ui texts
adb shell input keyevent KEYCODE_BACK; sleep 3

# settings
ui tap-id setting_button; sleep 4; shot 05-settings; echo "== screen 5 (settings)" >> "$OUT/ui-log.txt"; ui texts
adb shell input keyevent KEYCODE_BACK; sleep 3

# PLAY without an account: shows what the launcher says
ui tap-id play_button; sleep 6; shot 06-play; echo "== screen 6 (play)" >> "$OUT/ui-log.txt"; ui texts
echo "processes at end: $(running)" | tee -a "$OUT/alive.txt"

# Were the bundled mods and the Fabric version file placed in the game directory?
{
  G=/sdcard/Android/data/$PKG/files/.minecraft
  echo "--- ls -R $G (first 60 lines)"; adb shell "ls -R $G 2>&1 | head -60"
  echo "--- mods"; adb shell "ls -l $G/mods 2>&1"
  echo "--- launcher_profiles.json"; adb shell "cat $G/../.minecraft/launcher_profiles.json 2>&1 | head -20"
  echo "--- versions"; adb shell "ls -l $G/versions 2>&1"
} 2>&1 | tee "$OUT/game-files.txt"

# stop the recorder cleanly (SIGINT) so the MP4 gets finalised, then pull it
adb shell "pkill -2 screenrecord" ; sleep 6
adb pull /sdcard/rec.mp4 "$OUT/launcher-run.mp4" 2>&1 | tail -1
adb logcat -d -v threadtime > "$OUT/logcat-full.txt"
grep -E "pojav|Pojav|AndroidRuntime|FATAL|JREAuto|NewJRE|AsyncAsset|Internal" "$OUT/logcat-full.txt" | tail -n 150 > "$OUT/logcat-filtered.txt"
ls -l "$OUT"
exit 0
