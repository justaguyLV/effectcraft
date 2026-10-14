#!/usr/bin/env bash
# Builds Pojav's "jre-new" asset (Java 17: universal.tar.xz + bin-<arch>.tar.xz + version) from the
# last published JRE 17 builds. Pojav's CI artifacts for these have expired, the release files have not.
#   usage: build-jre.sh <output-dir>
set -euo pipefail
OUT="$(mkdir -p "$1" && cd "$1" && pwd)"
HERE="$(cd "$(dirname "$0")" && pwd)"
BASE=https://github.com/PojavLauncherTeam/android-openjdk-build-multiarch/releases/download
WORK="$(mktemp -d)"
mkdir -p "$WORK/in"
fetch() { curl -fsSL --retry 4 --retry-delay 3 -o "$WORK/in/$2" "$BASE/$1/$2"; }
fetch jre17-ca01427 jre17-arm64-20220817-release.tar.xz
fetch jre17-ec28559 jre17-arm-20210914-release.tar.xz
fetch jre17-ec28559 jre17-x86-20220225-release.tar.xz
fetch jre17-ec28559 jre17-x86_64-20210825-release.tar.xz
ls -l "$WORK/in"
TARGET_VERSION=17 bash "$HERE/repackjre.sh" "$WORK/in" "$OUT"
ls -l "$OUT"
for f in universal.tar.xz bin-arm.tar.xz bin-arm64.tar.xz bin-x86.tar.xz bin-x86_64.tar.xz version; do
  test -s "$OUT/$f" || { echo "missing $f"; exit 1; }
done
rm -rf "$WORK"
