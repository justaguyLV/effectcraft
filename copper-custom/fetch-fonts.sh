#!/usr/bin/env bash
# fetch-fonts.sh <font-res-dir>: downloads the fonts listed in fonts.txt from Google's official fonts repository
# (SIL OFL 1.1, Ubuntu Font Licence for Ubuntu). A missing optional font is skipped; a missing required one fails.
set -uo pipefail
D="$(mkdir -p "$1" && cd "$1" && pwd)"
HERE="$(cd "$(dirname "$0")" && pwd)"
BASE=https://raw.githubusercontent.com/google/fonts/main
fail=0; got=0
while read -r name path flag; do
  case "$name" in ''|'#'*) continue;; esac
  url="$BASE/$(python3 -c 'import sys,urllib.parse;print(urllib.parse.quote(sys.argv[1]))' "$path")"
  if curl -fsSL --retry 3 -o "$D/$name.ttf" "$url"; then
    magic=$(head -c 4 "$D/$name.ttf" | od -An -tx1 | tr -d ' \n')
    case "$magic" in 00010000|4f54544f|74727565) got=$((got + 1));; *) echo "not a font file: $name ($magic)"; rm -f "$D/$name.ttf"; [ "$flag" = required ] && fail=1;; esac
  else
    echo "could not fetch $name"; rm -f "$D/$name.ttf"; [ "$flag" = required ] && fail=1
  fi
done < "$HERE/fonts.txt"
echo "fonts fetched: $got"
du -sh "$D"
exit $fail
