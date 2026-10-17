#!/usr/bin/env bash
# Runs inside the emulator: installs the APK, opens the launcher, records a video and screenshots and dumps the
# on-screen texts (so the next run can drive the UI), plus the launcher's own log.
set -u
APK="$1"; OUT="${OUT:-emulator-out}"; PKG="${PKG:-com.maxjubayeryt.copper.debug}"
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$OUT"
shot() { adb exec-out screencap -p > "$OUT/$1.png" 2>/dev/null; echo "shot $1 $(stat -c %s "$OUT/$1.png") bytes"; }
ui() { python3 "$HERE/ui.py" "$@" >> "$OUT/ui-log.txt" 2>&1; tail -n 2 "$OUT/ui-log.txt"; }
running() { adb shell "ps -A | grep -c $PKG" | tr -d '\r'; }

adb wait-for-device
{ echo "android $(adb shell getprop ro.build.version.release | tr -d '\r') sdk $(adb shell getprop ro.build.version.sdk | tr -d '\r')"
  echo "abis $(adb shell getprop ro.product.cpu.abilist | tr -d '\r')"; } | tee "$OUT/device.txt"
adb install -r "$APK" 2>&1 | tee "$OUT/install.txt"
adb shell pm grant "$PKG" android.permission.POST_NOTIFICATIONS 2>/dev/null
adb logcat -c

( adb shell screenrecord --time-limit 170 --bit-rate 3000000 --size 720x1280 /sdcard/rec.mp4 >/dev/null 2>&1 & )
sleep 2
adb shell monkey -p "$PKG" -c android.intent.category.LAUNCHER 1 2>&1 | tee "$OUT/start.txt"
sleep 25; shot 01-start;  echo "== screen 1" >> "$OUT/ui-log.txt"; ui texts
echo "processes after start: $(running)" | tee "$OUT/alive.txt"
sleep 25; shot 02-after-wait; echo "== screen 2" >> "$OUT/ui-log.txt"; ui texts
# tap the middle of the screen once (storage / welcome dialogs often wait for a tap), then look again
adb shell input tap 360 900; sleep 6; shot 03-after-tap; echo "== screen 3" >> "$OUT/ui-log.txt"; ui texts
sleep 40; shot 04-later; echo "== screen 4" >> "$OUT/ui-log.txt"; ui texts
echo "processes at end: $(running)" | tee -a "$OUT/alive.txt"

# Were the bundled mods placed in the instance game directory?
{
  echo "--- instances (run-as)"; adb shell "run-as $PKG sh -c 'ls -R files 2>&1 | head -40'"
  echo "--- external"; adb shell "ls -R /sdcard/Android/data/$PKG/files 2>&1 | head -40"
} 2>&1 | tee "$OUT/game-files.txt"

adb shell "pkill -2 screenrecord"; sleep 6
adb pull /sdcard/rec.mp4 "$OUT/launcher-run.mp4" 2>&1 | tail -1
adb logcat -d -v threadtime > "$OUT/logcat-full.txt"
grep -E "copper|Copper|mojo|Mojo|AndroidRuntime|FATAL|AsyncAsset|Instances|Bundled" "$OUT/logcat-full.txt" | tail -n 200 > "$OUT/logcat-filtered.txt"
ls -l "$OUT"
exit 0
