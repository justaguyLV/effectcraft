#!/usr/bin/env bash
# Runs inside the emulator: installs the APK, drives the launcher a little, records a video and
# checks that the bundled Fabric/Meteor files were placed in the game directory.
set -u
APK="$1"; OUT="${OUT:-emulator-out}"; PKG=net.kdt.pojavlaunch.debug
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$OUT"
shot() { adb exec-out screencap -p > "$OUT/$1.png" 2>/dev/null; echo "shot $1 $(stat -c %s "$OUT/$1.png") bytes"; }
ui() { python3 "$HERE/ui.py" "$@" 2>&1 | tee -a "$OUT/ui-log.txt"; }

adb wait-for-device
{ echo "android $(adb shell getprop ro.build.version.release | tr -d '\r') sdk $(adb shell getprop ro.build.version.sdk | tr -d '\r')"
  echo "abis $(adb shell getprop ro.product.cpu.abilist | tr -d '\r')"; } | tee "$OUT/device.txt"
adb install -r "$APK" 2>&1 | tee "$OUT/install.txt"
adb logcat -c

# 150 s of video (the recorder's limit is 180 s)
( adb shell screenrecord --time-limit 150 --bit-rate 3000000 --size 720x1280 /sdcard/rec.mp4 >/dev/null 2>&1 & )
sleep 2
adb shell monkey -p "$PKG" -c android.intent.category.LAUNCHER 1 2>&1 | tee "$OUT/start.txt"
sleep 30; shot 01-start; echo "== screen 1" >> "$OUT/ui-log.txt"; ui texts
echo "pid: $(adb shell pidof $PKG | tr -d '\r')" | tee "$OUT/alive.txt"

ui tap-id account_spinner; sleep 3; shot 02-accounts; echo "== screen 2" >> "$OUT/ui-log.txt"; ui texts
ui tap-text "add account"; sleep 3; shot 03-add-account; echo "== screen 3" >> "$OUT/ui-log.txt"; ui texts
adb shell input keyevent KEYCODE_BACK; sleep 2; adb shell input keyevent KEYCODE_BACK; sleep 3
ui tap-id mc_version_spinner || ui tap-text "meteor"; sleep 3; shot 04-profiles; echo "== screen 4" >> "$OUT/ui-log.txt"; ui texts
adb shell input keyevent KEYCODE_BACK; sleep 3
ui tap-id play_button; sleep 12; shot 05-play; echo "== screen 5" >> "$OUT/ui-log.txt"; ui texts
echo "pid at end: $(adb shell pidof $PKG | tr -d '\r')" | tee -a "$OUT/alive.txt"

# Were the bundled mods and the Fabric version file placed in the game directory?
{
  echo "--- run-as"; adb shell "run-as $PKG sh -c 'find . -maxdepth 6 \( -name \"*.jar\" -path \"*mods*\" -o -name \"fabric-loader*.json\" -o -name launcher_profiles.json \) 2>/dev/null'"
  echo "--- /sdcard/Android/data"; adb shell "find /sdcard/Android/data/$PKG -maxdepth 6 \( -name '*.jar' -path '*mods*' -o -name 'fabric-loader*.json' -o -name launcher_profiles.json \) 2>/dev/null"
  echo "--- profiles"; adb shell "cat /sdcard/Android/data/$PKG/files/.minecraft/launcher_profiles.json 2>/dev/null || run-as $PKG cat files/.minecraft/launcher_profiles.json 2>/dev/null"
} 2>&1 | tee "$OUT/game-files.txt"

# let the recording finish, then pull it
sleep $(( 150 - 60 > 0 ? 40 : 5 )); sleep 20
adb pull /sdcard/rec.mp4 "$OUT/launcher-run.mp4" 2>&1 | tail -1
adb logcat -d -v threadtime > "$OUT/logcat-full.txt"
grep -E "pojav|Pojav|AndroidRuntime|FATAL|JREAuto|NewJRE|AsyncAsset|Internal" "$OUT/logcat-full.txt" | tail -n 150 > "$OUT/logcat-filtered.txt"
ls -l "$OUT"
exit 0
