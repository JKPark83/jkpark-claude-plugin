---
name: tech-blog-writer
description: >-
  Use when the user wants to write or draft a technical blog post (기술 블로그)
  — turning a topic, or an existing article/URL, into a polished, image-rich,
  junior-developer-friendly Korean blog post rendered as HTML. Triggers on
  openers like "이 주제로 기술 블로그 써줘", "이 링크 글로 정리해줘", "이거
  블로그 글로 써줘", "블로그 글 작성해줘", "write a blog post about", or "turn
  this article into a blog post". Reads the source link, fills gaps with web
  deep-search, translates English sources into natural Korean, embeds relevant
  images with attribution, renders clean HTML, and publishes to a remembered
  target (GitHub Pages repo or CMS paste).
---

# Tech Blog Writer

Turn a topic or a source article into a finished **technical blog post**: well
researched, written for a **junior developer**, generously **illustrated with
images**, output as **HTML**, and published to wherever the user usually posts.

**Language rule:** This skill file is written in English, but **everything the
reader and the user see MUST be in Korean (한국어)** — the blog post itself, its
headings, captions, and every question you ask. Keep code, identifiers, and
established English technical terms as-is. Internal reasoning can be any language.

## Inputs — what the user gives you

One of:

- a **topic** (e.g. "React Server Components"),
- one or more **source URLs** (an article, docs page, release notes), or
- a **rough draft** to polish.

Start by restating in **one Korean sentence** what you'll write and confirm the
angle, depth, and rough length. Don't over-interview — one quick confirmation,
then move.

## Workflow

1. Understand the source / topic
2. Research & fill gaps (parallel web search)
3. Outline (quick confirm)
4. Write — junior-friendly, natural Korean
5. Find & embed images (web search + attribution)
6. Render to HTML
7. Publish to a remembered target

### 1. Understand the source

- **URL given →** `WebFetch` it. Pull out the core thesis, key points, code,
  numbers. Note what's missing, outdated, or assumed.
- **Topic only →** sketch what a junior reader needs to follow it, and mark
  where your own knowledge is thin or possibly stale.

### 2. Research & fill gaps (don't guess)

List 3–6 sub-questions whose answers you must not invent — current version
numbers, API limits, benchmarks, common pitfalls, alternatives, best practices.

Fan them out as **parallel background research**: use the **Agent** tool with
`subagent_type: "general-purpose"`, **one agent per sub-question**, **all in a
single message**, `run_in_background: true`. Give each a tight prompt: the exact
question + *"Use WebSearch for current sources. Return 4–6 bullet findings, each
with a source link."*

- Verify any surprising or load-bearing claim against **2+ independent sources**.
- Keep **every source URL** — they become the 참고 자료 section.

### 3. Outline (quick confirm)

Propose a short Korean outline (sections + a one-line description each) and ask
the user to confirm or tweak. Keep it tight — don't stall the writing.

Default skeleton (adapt freely):

```
도입 — 왜 중요한가 / 어떤 문제를 푸는가 (독자를 끌어들이는 훅)
배경 / 사전 지식 — 따라오는 데 필요한 최소한만
본론 — 섹션별 설명 + 코드 + 이미지
실전 예제 / 적용 — 직접 해볼 수 있는 형태
흔한 실수 · 팁
마무리 — TL;DR 요약
참고 자료 — 리서치에 쓴 출처 링크
```

### 4. Write — voice, level, translation

**Before writing, read `references/translation-and-style.md`** for the
natural-translation rules and the junior-audience checklist.

Core rules:

- **Audience = junior developer.** They know basic programming; explain
  intermediate-and-up concepts, jargon, and *why it matters*. Use analogies.
  Don't waste words explaining trivia (what a variable or for-loop is).
- **Natural Korean translation.** When the source is English, translate the
  *meaning*, not the words. Avoid 번역투. Keep code, identifiers, and settled
  English terms (commit, deploy, cache, …) as-is or in their common Korean form.
- **Traceability.** Anything that came from research should be backed by a link
  in 참고 자료.

### 5. Images — search the web & attribute

The user wants **image-rich** posts. For each section that benefits, find a
relevant image, diagram, screenshot, or chart via `WebSearch` (use
image-oriented queries) and confirm the source with `WebFetch`.

- **Prefer reusable sources:** official docs/repos, the project's own assets,
  Wikimedia Commons, Unsplash/Pexels, or posts that clearly permit embedding.
  **Avoid clearly copyrighted images** used without permission.
- **Always wrap with attribution:**
  ```html
  <figure>
    <img src="..." alt="설명" loading="lazy">
    <figcaption>그림 설명 — 출처: <a href="원본링크" rel="nofollow">출처명</a></figcaption>
  </figure>
  ```
- **Hotlinking caution:** for **GitHub Pages**, prefer downloading the image
  into the repo's assets folder and referencing it locally (tell the user); for
  **CMS paste**, an external URL is usually fine — still attribute and respect
  the license.
- **No good licensed image?** Don't force a copyrighted one. Insert a captioned
  placeholder `<!-- 이미지 필요: <무엇을 보여줄지> -->` or a simple inline SVG /
  Mermaid diagram instead.
- Aim for **roughly one strong visual per major section**. Don't pad with
  irrelevant stock photos.

### 6. Render to HTML

**Read `references/html-templates.md`** and pick the output shape by target:

- **GitHub Pages / static repo →** first **inspect an existing post in the repo**
  and match its format (front matter, file naming, asset paths). If it's a plain
  HTML site, use the **standalone template**.
- **CMS paste →** use the **body-fragment template** (no `<html>`/`<head>`;
  minimal markup the editor won't strip).

Code blocks use `<pre><code class="language-xxx">…</code></pre>`; the standalone
template may load highlight.js from a CDN. Keep markup semantic, accessible,
responsive, and set `lang="ko"`.

### 7. Publish — ask, remember, reuse

Config file: **`~/.claude/blog-writer/targets.json`** (create the dir and file
if missing — `mkdir -p ~/.claude/blog-writer`).

**On publish:**

1. Read the config.
   - **Saved targets exist →** ask in Korean, suggesting the most-used one first:
     *"지난번처럼 **<name>**(<type>)에 올릴까요? 아니면 다른 곳에 올릴까요?"* —
     list the remembered targets + a "새 대상" option.
   - **None →** ask where to publish (GitHub Pages repo, or CMS paste).
2. Execute by target type:
   - **`github-pages`** — write the HTML file into `repoPath/postsDir` using the
     repo's naming convention, download any embedded images into its assets, then
     **`git add` / `commit` / `push` only after explicit confirmation**. Report
     the resulting public URL (`publicUrlBase` + slug).
   - **`cms`** — save the fragment to `./blog-out/<slug>.html` and offer to copy
     it to the clipboard (`pbcopy < file` on macOS). Tell the user to paste it
     into the editor.
3. **New target →** after a successful publish, ask *"이 대상을 다음에도 쓰게
   저장할까요?"* and append it, setting `lastUsed` to today's date (from session
   context) and `useCount: 1`. **Existing target →** bump `useCount` and update
   `lastUsed`.

**Never `git push` without explicit confirmation.**

Config schema:

```json
{
  "targets": [
    {
      "name": "my-github-blog",
      "type": "github-pages",
      "repoPath": "/Users/<you>/path/to/blog",
      "postsDir": "_posts",
      "assetsDir": "assets/img",
      "branch": "main",
      "publicUrlBase": "https://<user>.github.io/blog/",
      "useCount": 3,
      "lastUsed": "2026-06-18"
    },
    {
      "name": "velog",
      "type": "cms",
      "platform": "velog",
      "note": "본문 fragment를 에디터에 붙여넣기",
      "useCount": 5,
      "lastUsed": "2026-06-18"
    }
  ]
}
```

## Style

- Confirm scope and outline **fast**, then do the research, writing, and imaging
  autonomously — don't ping the user for every paragraph.
- When done, show the finished post (or its file path) and the publish result
  (public URL, or "clipboard에 복사됨 — 에디터에 붙여넣으세요").
- Stay in Korean with the user throughout.
