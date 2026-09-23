#!/usr/bin/env bash
# obs-html 스크린샷 자가 검수 — 헤드리스 Chrome으로 데스크톱·모바일 × 라이트·다크 + JS 꺼짐을 찍는다.
# 사용법: snap.sh <index.html> <출력폴더> [높이=4000]
# - 헤드리스 창은 폭 500px 밑으로 줄지 않아서, 모바일(390px)은 iframe 안에 띄워 찍는다.
# - preferredColorScheme: 0=다크, 1=라이트.
# - desktop-nojs: HTML 뷰어가 스크립트를 막아도 내용이 다 보이는지 확인용.
set -euo pipefail

html="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
out="$2"
h="${3:-4000}"
mkdir -p "$out"
out="$(cd "$out" && pwd)"

chrome=""
for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
         "/Applications/Chromium.app/Contents/MacOS/Chromium" \
         "$(command -v google-chrome 2>/dev/null || true)" \
         "$(command -v chromium 2>/dev/null || true)"; do
  [ -n "$c" ] && [ -x "$c" ] && { chrome="$c"; break; }
done
[ -n "$chrome" ] || { echo "Chrome/Chromium을 찾지 못했다 — 스크린샷 검수를 건너뛴다" >&2; exit 2; }

wrap="$out/_mobile.html"
cat > "$wrap" <<EOF
<!DOCTYPE html><html><body style="margin:0;background:#888">
<iframe src="file://$html" style="width:390px;height:${h}px;border:0;display:block"></iframe>
</body></html>
EOF

shot() { # 이름 폭 대상 추가옵션…
  local name="$1" w="$2" target="$3"; shift 3
  "$chrome" --headless=new --disable-gpu --hide-scrollbars --virtual-time-budget=1500 \
    --window-size="$w,$h" --screenshot="$out/$name.png" "$@" "$target" >/dev/null 2>&1
  echo "$out/$name.png"
}

shot desktop-light 1280 "file://$html" --blink-settings=preferredColorScheme=1
shot desktop-dark  1280 "file://$html" --blink-settings=preferredColorScheme=0
shot mobile-light  500  "file://$wrap" --blink-settings=preferredColorScheme=1
shot mobile-dark   500  "file://$wrap" --blink-settings=preferredColorScheme=0
# JS 꺼짐: 헤드리스 스크린샷은 scriptEnabled=false에서 실패하므로 <script>를 뺀 사본을 같은 폴더에 만들어 찍는다
nojs="$(dirname "$html")/.snap-nojs.html"
perl -0pe 's#<script\b.*?</script>##gs' "$html" > "$nojs"
shot desktop-nojs  1280 "file://$nojs" --blink-settings=preferredColorScheme=1
rm -f "$wrap" "$nojs"
