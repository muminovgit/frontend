#!/bin/bash
# Renders ../svg/*.svg to ../png/*.png at their native size with headless Chrome (or Chrome for Testing).
set -e
cd "$(dirname "$0")"
CHROME="${CHROME:-}"
for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
         "$HOME"/Library/Caches/ms-playwright/chromium-*/chrome-mac*/"Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing" \
         "$(command -v chromium || true)" "$(command -v google-chrome || true)"; do
  if [ -z "$CHROME" ] && [ -x "$c" ]; then CHROME="$c"; fi
done
[ -z "$CHROME" ] && { echo "Chrome topilmadi: CHROME=/yo'l/chrome ./render.sh"; exit 1; }
mkdir -p ../png
PROFILE="$(mktemp -d)"; trap 'rm -rf "$PROFILE"' EXIT
for f in ../svg/*.svg; do
  n=$(basename "$f" .svg)
  read w h < <(python3 -c 'import re,sys; print(*re.search(r"viewBox=\"0 0 (\d+) (\d+)\"", open(sys.argv[1]).read(4000)).groups())' "$f")
  html="$(mktemp -t brand).html"
  printf '<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;overflow:hidden}img{display:block}</style></head><body><img src="file://%s" width="%s" height="%s"></body></html>' "$(cd ../svg && pwd)/$n.svg" "$w" "$h" > "$html"
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --allow-file-access-from-files --user-data-dir="$PROFILE" --no-first-run \
    --window-size="$w,$h" --screenshot="$(pwd)/../png/$n.png" "file://$html" >/dev/null 2>&1 || true
  [ -s "../png/$n.png" ] || { echo "xato: $n render bo'lmadi"; exit 1; }
  rm -f "$html"
  echo "png $n ${w}x${h}"
done
