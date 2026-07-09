# HTML 템플릿 (obs-html 6단계)

Obsidian 볼트에 들어가는 문서다. **외부 의존이 하나도 없어야 한다** — 볼트는
오프라인에서 열리고, CDN 링크는 언젠가 깨진다.

## 규칙

- 완전한 단일 HTML 파일 (`<!DOCTYPE html>` … `</html>`), `lang="ko"`
- CSS는 전부 `<style>` 안에 인라인. **외부 스타일시트·폰트·스크립트 금지**
- 이미지: 상대 경로 `assets/…`, 인라인 `<svg>`, 또는 `data:` URI
- 라이트/다크 모두 대응
- 한국어 줄바꿈을 위해 `word-break: keep-all`

## 기본 템플릿

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{제목}}</title>
  <meta name="description" content="{{한 줄 요약}}">
  <style>
    :root {
      color-scheme: light dark;
      --bg: #ffffff; --fg: #24292f; --muted: #6b7280;
      --border: #e5e7eb; --code-bg: #f6f8fa; --link: #0969da;
      --accent: #0969da; --note-bg: #f6f8fa;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --bg: #1e1e1e; --fg: #e6e6e6; --muted: #9aa0a6;
        --border: #3a3a3a; --code-bg: #2a2a2a; --link: #6cb6ff;
        --accent: #6cb6ff; --note-bg: #262626;
      }
    }
    * { box-sizing: border-box; }
    body {
      max-width: 820px; margin: 0 auto; padding: 2rem 1.2rem;
      background: var(--bg); color: var(--fg);
      font-family: -apple-system, "Apple SD Gothic Neo", "Noto Sans KR", system-ui, sans-serif;
      line-height: 1.8; word-break: keep-all;
    }
    h1 { font-size: 2rem; line-height: 1.35; margin: 0 0 .6rem; }
    h2 { margin-top: 2.8rem; padding-bottom: .35rem; border-bottom: 1px solid var(--border); }
    h3 { margin-top: 2rem; }
    p, li { font-size: 1.05rem; }
    a { color: var(--link); }
    .subtitle { color: var(--muted); margin-top: 0; }
    pre {
      background: var(--code-bg); padding: 1rem; border-radius: 8px;
      overflow-x: auto; font-size: .9rem; line-height: 1.6;
    }
    code:not(pre code) {
      background: var(--code-bg); padding: .15em .4em; border-radius: 4px; font-size: .9em;
    }
    figure { margin: 2rem 0; text-align: center; }
    figure img, figure svg { max-width: 100%; height: auto; border-radius: 8px; }
    figcaption { font-size: .85rem; color: var(--muted); margin-top: .6rem; }
    blockquote {
      margin: 1.6rem 0; padding: .6rem 1rem;
      border-left: 4px solid var(--accent); background: var(--note-bg);
      border-radius: 0 6px 6px 0; color: var(--fg);
    }
    table { border-collapse: collapse; width: 100%; display: block; overflow-x: auto; }
    th, td { border: 1px solid var(--border); padding: .5rem .8rem; text-align: left; }
    th { background: var(--note-bg); }
    .tldr { background: var(--note-bg); border-radius: 8px; padding: 1rem 1.2rem; }
  </style>
</head>
<body>
  <article>
    <h1>{{제목}}</h1>
    <p class="subtitle">{{한 줄 요약}}</p>

    <!-- 섹션마다: h2 + 문단 + figure(그림 최소 1개) + (기술 문서면) 코드 -->

    <h2>마무리</h2>
    <div class="tldr">
      <p><strong>한눈에 보기</strong></p>
      <ul><li>{{요점}}</li></ul>
    </div>

    <h2>참고 자료</h2>
    <ul><li><a href="{{링크}}" rel="nofollow">{{출처 제목}}</a></li></ul>
  </article>
</body>
</html>
```

## 그림 넣는 법

**웹 이미지** — 볼트 폴더 안 `assets/`로 내려받고 상대 경로로 참조한다.

```html
<figure>
  <img src="assets/flow.png" alt="요청 처리 흐름도" loading="lazy">
  <figcaption>그림 1. 요청 처리 흐름 — 출처: <a href="{{원본}}" rel="nofollow">{{출처명}}</a></figcaption>
</figure>
```

**직접 그린 SVG** — 구조·흐름 설명의 기본 선택지. `currentColor`를 쓰면 다크
모드에서도 그대로 읽힌다.

```html
<figure>
  <svg viewBox="0 0 480 120" role="img" aria-label="요청 처리 흐름도" fill="none"
       stroke="currentColor" stroke-width="1.5" font-size="13">
    <rect x="10"  y="35" width="110" height="50" rx="8"/>
    <text x="65"  y="65" text-anchor="middle" stroke="none" fill="currentColor">클라이언트</text>
    <rect x="185" y="35" width="110" height="50" rx="8"/>
    <text x="240" y="65" text-anchor="middle" stroke="none" fill="currentColor">API 서버</text>
    <rect x="360" y="35" width="110" height="50" rx="8"/>
    <text x="415" y="65" text-anchor="middle" stroke="none" fill="currentColor">DB</text>
    <path d="M120 60 H185"  marker-end="url(#a)"/>
    <path d="M295 60 H360" marker-end="url(#a)"/>
    <defs>
      <marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
        <path d="M0 0 L7 3 L0 6 z" fill="currentColor" stroke="none"/>
      </marker>
    </defs>
  </svg>
  <figcaption>그림 1. 요청 처리 흐름 — 출처: 직접 작성</figcaption>
</figure>
```

**차트** — 수치 비교는 인라인 SVG 막대/선 차트로. 그리기 전에 `dataviz` 스킬을
읽어 색상·축·범례 규칙을 맞춘다.

## 코드 블록

```html
<pre><code class="language-python">async def handler(req):
    return {"ok": True}
</code></pre>
```

하이라이팅 라이브러리는 붙이지 않는다 (외부 스크립트 금지). `class="language-*"`는
남겨두면 나중에 다른 곳에 옮겨 붙일 때 쓸모가 있다.
