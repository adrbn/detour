#!/usr/bin/env bash
# Captures the real Detour menu view in its six states, light and dark, into docs/assets/readme-src/states.
# The app opens the windows behind the desktop (--render-states); screencapture grabs each one by its id.
# -AppleAccentColor 4 draws with macOS's default blue accent, whatever the Mac is set to.
# Optional argument: a language code (fr, ja…) to capture that localization into states-<code>.
set -euo pipefail
cd "$(dirname "$0")/.."
LANGUAGE="${1:-en}"
swift build -c release >/dev/null
# A bare executable reads its localizations from the folder it sits in.
cp -R Resources/*.lproj .build/release/
WORK=$(mktemp -d)
.build/release/Detour --render-states "$WORK" -AppleAccentColor 4 -AppleLanguages "($LANGUAGE)" &
APP=$!
for _ in $(seq 40); do [ -s "$WORK/windows.txt" ] && break; sleep 0.1; done
OUT=docs/assets/readme-src/states
[ "$LANGUAGE" = en ] || OUT="$OUT-$LANGUAGE"
mkdir -p "$OUT"
while read -r name id; do
    # The window server takes a moment before a new window can be captured.
    for _ in $(seq 20); do screencapture -x -o -l "$id" "$OUT/$name.png" 2>/dev/null && break; sleep 0.5; done
    [ -s "$OUT/$name.png" ] || { echo "could not capture $name" >&2; exit 1; }
done < "$WORK/windows.txt"
kill "$APP" 2>/dev/null || true
rm -rf "$WORK"
ls "$OUT"
