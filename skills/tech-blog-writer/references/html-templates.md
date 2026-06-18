# HTML templates

Read this at SKILL.md step 6. Two shapes — pick by publish target.

> For **GitHub Pages / static repos, inspect an existing post first** and match
> its real format (front matter, file naming, asset paths). These templates are
> the fallback when there's no existing convention to copy.

## A. Standalone document

Full self-contained HTML — opens in a browser as-is. Use for plain-HTML sites or
a quick local preview. Inline CSS so it needs no build step; highlight.js from a
CDN for code coloring.

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{제목}}</title>
  <meta name="description" content="{{한 줄 요약}}">
  <link rel="stylesheet"
        href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css">
  <style>
    :root { color-scheme: light dark; }
    body {
      max-width: 760px; margin: 0 auto; padding: 2rem 1.2rem;
      font-family: -apple-system, "Apple SD Gothic Neo", "Noto Sans KR", system-ui, sans-serif;
      line-height: 1.75; color: #24292f; word-break: keep-all;
    }
    h1 { font-size: 2rem; line-height: 1.3; margin-top: 0; }
    h2 { margin-top: 2.5rem; border-bottom: 1px solid #eaecef; padding-bottom: .3rem; }
    h3 { margin-top: 2rem; }
    p, li { font-size: 1.05rem; }
    a { color: #0969da; }
    pre {
      background: #f6f8fa; padding: 1rem; border-radius: 8px;
      overflow-x: auto; font-size: .9rem;
    }
    code:not(pre code) {
      background: #f0f1f3; padding: .15em .4em; border-radius: 4px; font-size: .9em;
    }
    figure { margin: 1.8rem 0; text-align: center; }
    figure img { max-width: 100%; height: auto; border-radius: 8px; }
    figcaption { font-size: .85rem; color: #6b7280; margin-top: .5rem; }
    blockquote {
      margin: 1.5rem 0; padding: .2rem 1rem; border-left: 4px solid #d0d7de; color: #57606a;
    }
    .tldr { background: #f6f8fa; border-radius: 8px; padding: 1rem 1.2rem; }
  </style>
</head>
<body>
  <article>
    <h1>{{제목}}</h1>
    <!-- 본문: 섹션별 h2/h3 + 문단 + 코드 + figure 이미지 -->
  </article>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
  <script>hljs.highlightAll();</script>
</body>
</html>
```

## B. CMS body fragment (Tistory / Velog / WordPress 등)

Paste-into-the-editor markup. **No `<html>`, `<head>`, `<style>`, or `<script>`**
— most CMS HTML editors strip or escape them. Keep markup plain and semantic so
the platform's own theme styles it. Use external image URLs (attributed).

```html
<h2>{{섹션 제목}}</h2>
<p>{{문단}}</p>

<pre><code class="language-ts">// 코드 예시
const x = 1;
</code></pre>

<figure>
  <img src="{{이미지 URL}}" alt="{{설명}}">
  <figcaption>{{그림 설명}} — 출처: <a href="{{원본}}" rel="nofollow">{{출처명}}</a></figcaption>
</figure>

<blockquote>💡 {{핵심 팁이나 주의사항}}</blockquote>

<h2>마무리</h2>
<div>
  <p><strong>TL;DR</strong></p>
  <ul>
    <li>{{요점 1}}</li>
    <li>{{요점 2}}</li>
  </ul>
</div>

<h2>참고 자료</h2>
<ul>
  <li><a href="{{링크}}">{{출처 제목}}</a></li>
</ul>
```

CMS notes:

- **Velog** renders Markdown natively — if posting there, Markdown is often
  cleaner than HTML; ask the user which they prefer. The fragment above still
  pastes fine in HTML mode.
- **Tistory / WordPress** have an HTML/"코드" mode — paste there, not the rich
  editor, or tags get escaped.
- Code highlighting depends on the platform's theme; don't rely on inline styles
  for it. Keep `class="language-xxx"` so theme highlighters can pick it up.
- Test one image and one code block first if the user is unsure how their
  platform handles pasted HTML.
