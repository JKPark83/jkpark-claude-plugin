#!/usr/bin/env python3
"""obs-html 결과물 정적 검사 — 표준 라이브러리만 쓴다.

사용법: python3 check_html.py <index.html>
종료 코드: 0 = 오류 없음(경고는 있을 수 있음), 1 = 오류 있음.

검사 항목
  오류: 외부 리소스, lang="ko" 누락, id 중복, img alt 누락, SVG 접근성 계약
        (role·첫 자식 title·desc·aria-labelledby), SVG 안 hex 색, 12px 미만 한글,
        박스를 넘치는 라벨(references/diagram-design.md §5 폭 산식)
  경고: 그림자, 캡션 없는 figure, 사선 <line>, 노드 9개·강조 2개 초과
"""
import re
import sys
from html.parser import HTMLParser

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
# 템플릿 .dg 텍스트 클래스의 글자 크기 — assets/template.html과 맞춘다
TEXT_SIZE = {"t": 13, "t-sub": 12, "t-tag": 10, "t-edge": 12, "t-zone": 12}
HANGUL = re.compile(r"[ᄀ-ᇿ㄰-㆏가-힣]")
PAD = 6  # 라벨이 박스 테두리에 붙지 않도록 남길 최소 여백(px)


class Node:
    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.parent = tag, dict(attrs), parent
        self.children, self.text, self.line = [], "", 0

    def cls(self):
        return set((self.attrs.get("class") or "").split())

    def walk(self):
        yield self
        for c in self.children:
            yield from c.walk()


class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", [], None)
        self.cur = self.root
        self.style_text = []

    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs, self.cur)
        n.line = self.getpos()[0]
        self.cur.children.append(n)
        if tag not in VOID:
            self.cur = n

    def handle_startendtag(self, tag, attrs):
        n = Node(tag, attrs, self.cur)
        n.line = self.getpos()[0]
        self.cur.children.append(n)

    def handle_endtag(self, tag):
        n = self.cur
        while n is not self.root and n.tag != tag:
            n = n.parent
        if n is not self.root:
            self.cur = n.parent

    def handle_data(self, data):
        self.cur.text += data
        if self.cur.tag == "style":
            self.style_text.append(data)


def text_width(s, size, mono):
    em = sum(1.0 if HANGUL.search(ch) or ord(ch) > 0x2E80 else (0.62 if mono else 0.6) for ch in s)
    return em * size


def num(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def main(path):
    src = open(path, encoding="utf-8").read()
    t = Tree()
    t.feed(src)
    errors, warns = [], []
    err = lambda line, msg: errors.append(f"  L{line}: {msg}")
    warn = lambda line, msg: warns.append(f"  L{line}: {msg}")
    nodes = list(t.root.walk())

    # 문서 기본
    html = next((n for n in nodes if n.tag == "html"), None)
    if not html or html.attrs.get("lang") != "ko":
        err(html.line if html else 1, '<html lang="ko">가 아니다')
    css = "\n".join(t.style_text)
    if "keep-all" not in css:
        err(1, "word-break: keep-all이 없다")
    if "prefers-color-scheme" not in css:
        err(1, "다크 모드(prefers-color-scheme) 규칙이 없다")

    # 외부 리소스
    ext = re.compile(r"^(https?:)?//", re.I)
    for n in nodes:
        a = n.attrs
        if n.tag == "script" and a.get("src"):
            err(n.line, f"외부/별도 스크립트: {a['src']}")
        if n.tag == "link" and "stylesheet" in (a.get("rel") or "") :
            err(n.line, f"외부 스타일시트: {a.get('href')}")
        if n.tag in ("img", "source", "video", "audio", "iframe", "embed") and ext.match(a.get("src") or ""):
            err(n.line, f"핫링크 리소스(assets/로 내려받을 것): {a.get('src')}")
        if n.tag == "img" and "alt" not in a:
            err(n.line, f"img에 alt가 없다: {a.get('src')}")
    for m in re.finditer(r"@import|url\(\s*['\"]?(https?:)?//", css):
        err(1, f"CSS 외부 참조: {m.group(0)}")

    # id 중복
    seen = {}
    for n in nodes:
        i = n.attrs.get("id")
        if i:
            if i in seen:
                err(n.line, f'id 중복 "{i}" (처음: L{seen[i]})')
            seen.setdefault(i, n.line)

    # 그림자
    if re.search(r"box-shadow\s*:\s*(?!none)", css) or "drop-shadow" in css:
        warn(1, "그림자 사용 — 테두리로 층을 나눈다 (diagram-design §5)")

    # figure
    for n in nodes:
        if n.tag == "figure" and not any(c.tag == "figcaption" for c in n.walk()):
            warn(n.line, "figure에 figcaption이 없다")

    # SVG
    for svg in (n for n in nodes if n.tag == "svg" and n.parent.tag != "svg"):
        a = svg.attrs
        kids = [c for c in svg.children]
        if a.get("role") != "img":
            err(svg.line, 'svg에 role="img"가 없다')
        if not kids or kids[0].tag != "title" or not kids[0].text.strip():
            err(svg.line, "svg의 첫 자식이 내용 있는 <title>이 아니다")
        if not any(c.tag == "desc" and c.text.strip() for c in kids):
            err(svg.line, "svg에 <desc>가 없다")
        for ref in (a.get("aria-labelledby") or "").split():
            if ref not in seen:
                err(svg.line, f'aria-labelledby가 없는 id "{ref}"를 가리킨다')
        if not a.get("aria-labelledby"):
            err(svg.line, "svg에 aria-labelledby가 없다")

        sub = list(svg.walk())
        for n in sub:
            for k in ("fill", "stroke", "stop-color", "color"):
                if re.match(r"#[0-9a-f]{3,8}$", n.attrs.get(k, ""), re.I):
                    err(n.line, f'svg 안 하드코딩 색 {k}="{n.attrs[k]}" — 클래스/변수를 쓴다')
            if n.tag == "line" and num(n.attrs.get("x1")) != num(n.attrs.get("x2")) and num(n.attrs.get("y1")) != num(n.attrs.get("y2")):
                warn(n.line, "사선 <line> — 직각 꺾임 path로 (diagram-design §4-1)")

        nodes_n = [n for n in sub if n.tag == "rect" and any(c.startswith("n-") and c != "n-zone" for c in n.cls())]
        focal = [n for n in sub if {"n-focal", "e-focal"} & n.cls()]
        if len(nodes_n) > 9:
            warn(svg.line, f"노드 {len(nodes_n)}개 > 9 — 개요/상세로 나눈다")
        if len(focal) > 2:
            warn(svg.line, f"강조 요소 {len(focal)}개 > 2")

        # 라벨 넘침: 텍스트 중심을 품는 가장 작은 rect 안에 들어가는가
        rects = []
        for r in sub:
            if r.tag != "rect" or not (r.cls() & ({"mask"} | {c for c in r.cls() if c.startswith("n-")})):
                continue
            rects.append((num(r.attrs.get("x")), num(r.attrs.get("y")), num(r.attrs.get("width")), num(r.attrs.get("height")), r))
        for tx in sub:
            if tx.tag != "text" or not tx.text.strip():
                continue
            if any("transform" in p.attrs for p in _ancestors(tx, svg)):
                continue
            c = tx.cls()
            size = next((TEXT_SIZE[k] for k in TEXT_SIZE if k in c), None)
            if size is None:
                continue
            s = tx.text.strip()
            if HANGUL.search(s) and size < 12:
                err(tx.line, f'한글 라벨 "{s}"가 {size}px — 12px 이상')
            w = text_width(s, size, "mono" in c)
            x, y = num(tx.attrs.get("x")), num(tx.attrs.get("y"))
            left = x - w / 2 if "c" in c else (x - w if "end" in c else x)
            cx = left + w / 2
            cy = y - size * 0.35
            box = [r for r in rects if r[0] <= cx <= r[0] + r[2] and r[1] <= cy <= r[1] + r[3]]
            if not box:
                continue
            bx, by, bw, bh, br = min(box, key=lambda r: r[2] * r[3])
            pad = 0 if "mask" in br.cls() else PAD
            if left < bx + pad - 0.5 or left + w > bx + bw - pad + 0.5:
                err(tx.line, f'라벨 "{s}" 추정 폭 {w:.0f}px가 박스(x={bx:.0f}, w={bw:.0f})를 넘친다')

    print(f"check_html: {path}")
    if errors:
        print(f"오류 {len(errors)}건")
        print("\n".join(errors))
    if warns:
        print(f"경고 {len(warns)}건")
        print("\n".join(warns))
    if not errors and not warns:
        print("통과 — 오류·경고 없음")
    return 1 if errors else 0


def _ancestors(n, stop):
    p = n.parent
    while p is not None and p is not stop:
        yield p
        p = p.parent


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
