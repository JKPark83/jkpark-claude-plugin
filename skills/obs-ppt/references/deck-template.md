# Slide deck template (obs-ppt Step 6)

A single self-contained HTML file destined for the Obsidian vault. **Zero
external dependencies** — no CDN scripts, stylesheets, or fonts. Open it in
a browser for presenting; print it for a PDF handout.

## Rules

- Complete single HTML file, `lang="ko"`, all CSS/JS inline
- Slides are designed at **960×540 (16:9)** and scaled to the viewport by JS
- Images: relative `assets/…` paths, inline `<svg>`, or `data:` URIs
- `word-break: keep-all` for Korean line breaking
- Light minimal palette: white slides, one accent color (`--accent`)
- Each slide is one `<section class="slide">`; its speaker notes live in a
  child `<aside class="notes">`

## Template

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{제목}}</title>
  <style>
    :root {
      --bg: #ffffff; --fg: #1f2328; --muted: #6b7280;
      --accent: #0969da; --accent-soft: #eaf3ff;
      --border: #e5e7eb; --code-bg: #f6f8fa; --stage-bg: #eef1f5;
    }
    * { box-sizing: border-box; }
    html, body { height: 100%; margin: 0; }
    body {
      background: var(--stage-bg); color: var(--fg); overflow: hidden;
      font-family: -apple-system, "Apple SD Gothic Neo", "Noto Sans KR", system-ui, sans-serif;
      word-break: keep-all;
    }
    .stage { position: fixed; inset: 0; display: flex; align-items: center; justify-content: center; }
    .slide {
      width: 960px; height: 540px; flex: 0 0 auto; position: absolute;
      background: var(--bg); border-radius: 12px;
      box-shadow: 0 8px 30px rgba(0,0,0,.12);
      padding: 48px 64px; display: none; flex-direction: column;
    }
    .slide.active { display: flex; }
    .slide h1 { font-size: 46px; line-height: 1.3; margin: 0 0 16px; }
    .slide h2 {
      font-size: 30px; line-height: 1.35; margin: 0 0 28px;
      padding-bottom: 12px; border-bottom: 3px solid var(--accent);
    }
    .slide ul, .slide ol { margin: 0; padding-left: 1.2em; font-size: 22px; line-height: 1.7; }
    .slide li { margin-bottom: .5em; }
    .slide li::marker { color: var(--accent); }
    .slide p { font-size: 22px; line-height: 1.7; margin: 0 0 .6em; }
    .slide pre {
      background: var(--code-bg); padding: 16px 20px; border-radius: 8px;
      font-size: 17px; line-height: 1.55; overflow: hidden; margin: 0;
    }
    .slide code:not(pre code) {
      background: var(--code-bg); padding: .1em .35em; border-radius: 4px; font-size: .92em;
    }
    .slide figure { margin: auto 0; text-align: center; }
    .slide figure img, .slide figure svg { max-width: 100%; max-height: 300px; }
    .slide figcaption { font-size: 15px; color: var(--muted); margin-top: 8px; }
    .muted { color: var(--muted); }
    .accent { color: var(--accent); }
    .cols { display: flex; gap: 32px; }
    .cols > * { flex: 1; min-width: 0; }
    .title-slide { justify-content: center; text-align: center; }
    .title-slide .subtitle { font-size: 24px; color: var(--muted); }
    .title-slide .meta { font-size: 18px; color: var(--muted); margin-top: 48px; }
    .badge {
      display: inline-block; background: var(--accent-soft); color: var(--accent);
      font-size: 16px; font-weight: 600; padding: 4px 14px; border-radius: 999px;
      margin-bottom: 20px; align-self: flex-start;
    }
    .slide .notes { display: none; }

    /* HUD: prev/next, counter, notes toggle */
    .hud {
      position: fixed; left: 0; right: 0; bottom: 14px;
      display: flex; align-items: center; justify-content: center; gap: 14px;
      font-size: 14px; color: var(--muted); z-index: 10;
    }
    .hud button {
      border: 1px solid var(--border); background: var(--bg); color: var(--fg);
      border-radius: 8px; padding: 6px 14px; font-size: 14px; cursor: pointer;
    }
    .hud button:hover { border-color: var(--accent); color: var(--accent); }

    /* Speaker-notes panel (filled by JS from the active slide) */
    #notes-panel {
      position: fixed; left: 50%; transform: translateX(-50%);
      bottom: 56px; width: min(880px, 92vw); max-height: 26vh; overflow-y: auto;
      background: var(--bg); border: 1px solid var(--border); border-radius: 10px;
      box-shadow: 0 6px 24px rgba(0,0,0,.14);
      padding: 14px 20px; font-size: 16px; line-height: 1.7; z-index: 9;
    }
    #notes-panel[hidden] { display: none; }
    #notes-panel .label { font-size: 12px; font-weight: 700; color: var(--accent); }

    /* Print: one slide per page, notes below — a PDF handout */
    @media print {
      body { overflow: visible; background: #fff; }
      .stage { position: static; display: block; }
      .slide {
        display: flex; position: static; transform: none !important;
        width: 100%; height: auto; min-height: 540px; margin: 0 0 24px;
        box-shadow: none; border: 1px solid var(--border);
        page-break-after: always;
      }
      .slide .notes {
        display: block; margin-top: auto; padding-top: 14px;
        border-top: 1px dashed var(--border);
        font-size: 15px; line-height: 1.7; color: var(--muted);
      }
      .hud, #notes-panel { display: none !important; }
    }
  </style>
</head>
<body>
<div class="stage">

  <!-- 1. Title slide -->
  <section class="slide title-slide">
    <h1>{{제목}}</h1>
    <p class="subtitle">{{부제 — 한 줄 요약}}</p>
    <p class="meta">{{발표자·날짜 등, 필요 시}}</p>
    <aside class="notes">{{이 발표의 목적과 배경을 2~3문장으로.}}</aside>
  </section>

  <!-- 2. Agenda -->
  <section class="slide">
    <h2>목차</h2>
    <ol>
      <li>{{섹션 1}}</li>
      <li>{{섹션 2}}</li>
    </ol>
    <aside class="notes">{{진행 순서를 한 문장으로.}}</aside>
  </section>

  <!-- Content slide: bullets -->
  <section class="slide">
    <span class="badge">{{섹션명}}</span>
    <h2>{{결론이 보이는 제목}}</h2>
    <ul>
      <li>{{요점 — 최대 5개, 각 2줄 이내}}</li>
    </ul>
    <aside class="notes">{{말로 풀어 설명할 2~5문장. 근거·수치·출처는 여기에.}}</aside>
  </section>

  <!-- Content slide: diagram -->
  <section class="slide">
    <span class="badge">{{섹션명}}</span>
    <h2>{{제목}}</h2>
    <figure>
      <svg viewBox="0 0 480 120" role="img" aria-label="{{설명}}" fill="none"
           stroke="currentColor" stroke-width="1.5" font-size="13">
        <rect x="10" y="35" width="110" height="50" rx="8"/>
        <text x="65" y="65" text-anchor="middle" stroke="none" fill="currentColor">{{A}}</text>
        <rect x="185" y="35" width="110" height="50" rx="8"/>
        <text x="240" y="65" text-anchor="middle" stroke="none" fill="currentColor">{{B}}</text>
        <path d="M120 60 H185" marker-end="url(#arr)"/>
        <defs>
          <marker id="arr" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
            <path d="M0 0 L7 3 L0 6 z" fill="currentColor" stroke="none"/>
          </marker>
        </defs>
      </svg>
      <figcaption>그림 1. {{캡션}} — 출처: 직접 작성</figcaption>
    </figure>
    <aside class="notes">{{그림이 보여주는 것을 설명.}}</aside>
  </section>

  <!-- Two-column slide (comparison, code + explanation) -->
  <section class="slide">
    <h2>{{제목}}</h2>
    <div class="cols">
      <div><ul><li>{{왼쪽}}</li></ul></div>
      <div><pre><code>{{코드 또는 오른쪽 내용}}</code></pre></div>
    </div>
    <aside class="notes">{{노트}}</aside>
  </section>

  <!-- Summary -->
  <section class="slide">
    <h2>정리</h2>
    <ul>
      <li>{{핵심 요약 3~5개}}</li>
    </ul>
    <aside class="notes">{{마무리 멘트.}}</aside>
  </section>

  <!-- Sources (new-topic) / original link (conversion) -->
  <section class="slide">
    <h2>출처</h2>
    <ul class="muted" style="font-size:18px">
      <li><a href="{{링크}}" rel="nofollow">{{출처 제목}}</a></li>
    </ul>
    <aside class="notes"></aside>
  </section>

</div>

<div class="hud">
  <button id="prev" aria-label="이전 슬라이드">◀</button>
  <span id="counter">1 / 1</span>
  <button id="next" aria-label="다음 슬라이드">▶</button>
  <button id="notes-btn">노트 (N)</button>
</div>
<div id="notes-panel" hidden><span class="label">발표자 노트</span><div id="notes-body"></div></div>

<script>
  (function () {
    var slides = Array.prototype.slice.call(document.querySelectorAll('.slide'));
    var counter = document.getElementById('counter');
    var panel = document.getElementById('notes-panel');
    var notesBody = document.getElementById('notes-body');
    var i = Math.min(Math.max(parseInt(location.hash.slice(1), 10) - 1 || 0, 0), slides.length - 1);

    function fit() {
      var k = Math.min(window.innerWidth * 0.94 / 960, window.innerHeight * 0.86 / 540);
      slides.forEach(function (s) { s.style.transform = 'scale(' + k + ')'; });
    }

    function show(n) {
      i = Math.min(Math.max(n, 0), slides.length - 1);
      slides.forEach(function (s, j) { s.classList.toggle('active', j === i); });
      counter.textContent = (i + 1) + ' / ' + slides.length;
      location.hash = i + 1;
      var notes = slides[i].querySelector('.notes');
      notesBody.innerHTML = notes ? notes.innerHTML : '<span class="muted">노트 없음</span>';
    }

    document.getElementById('prev').onclick = function () { show(i - 1); };
    document.getElementById('next').onclick = function () { show(i + 1); };
    document.getElementById('notes-btn').onclick = function () { panel.hidden = !panel.hidden; };

    document.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') { e.preventDefault(); show(i + 1); }
      else if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); show(i - 1); }
      else if (e.key === 'Home') { show(0); }
      else if (e.key === 'End') { show(slides.length - 1); }
      else if (e.key === 'n' || e.key === 'N') { panel.hidden = !panel.hidden; }
    });

    window.addEventListener('resize', fit);
    fit();
    show(i);
  })();
</script>
</body>
</html>
```

## Notes on using the template

- Duplicate the content-slide sections as needed; keep every slide's
  `<aside class="notes">` — even a one-liner — so the notes panel and the
  printed handout stay complete.
- Code on slides: trim to the essential lines (≤12); the full snippet can go
  into the folder-note `.md` instead. No highlighting library — the plain
  `--code-bg` block is enough.
- Charts: read the `dataviz` skill first, then draw inline SVG using
  `currentColor` strokes so the light palette stays consistent.
- Keep total file size reasonable: prefer SVG over PNG; if a photo is
  unavoidable, downscale before saving into `assets/`.
