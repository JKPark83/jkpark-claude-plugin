---
name: obs-ppt
description: >-
  Use when the user wants presentation slides — a PPT-style HTML slide deck —
  created and filed into their Obsidian vault, either by researching a new
  topic or by converting an existing document, note, or analysis into slides.
  Triggers on "PPT 형식 HTML 만들어줘", "슬라이드로 정리해서 obs에 저장해줘",
  "발표자료 만들어줘", "이 문서를 슬라이드로 변환해줘", "프레젠테이션으로
  만들어줘", "obs-ppt", "/obs-ppt". Not for ordinary article-style HTML
  write-ups (use obs-html for those). Always interviews the user first
  (AskUserQuestion) to pin down slide count and requirements, writes concise
  natural Korean (one idea per slide, prose moved into toggleable speaker
  notes), renders a self-contained single-file 16:9 deck with keyboard/button
  navigation and a page counter in a light minimal design, then hands the
  finished deck to the obs skill for folder-note filing and Home.md indexing.
---

# obs-ppt — PPT-style HTML slide deck, filed into Obsidian

Takes either **a topic to research** or **an existing document/note to
convert**, turns it into a **self-contained single-file HTML slide deck**
(fullscreen one-slide-at-a-time, keyboard/button navigation, toggleable
speaker notes), and **saves it into the Obsidian vault via the `obs` skill**.

This skill file is in English, but **everything the user sees — slide text,
titles, speaker notes, interview questions, the final report — must be in
Korean.** Keep code, identifiers, and established English tech terms
(commit, cache, deploy …) as-is.

## Hard rules

1. **Never start writing without the interview.** Violation: the user says
   "이거 PPT로 만들어줘" and you immediately generate 12 slides — wrong.
   Confirm slide count and audience first (Step 1).
2. **One idea per slide — no paragraphs on slides.** A slide body holds at
   most ~5 bullets, each ≤2 lines. Violation: pasting a 6-sentence paragraph
   from the source document onto a slide. Prose belongs in the speaker notes.
3. **Conversion mode adds no facts.** Slides built from an existing document
   may only contain facts present in that source (reorganizing and
   compressing is fine). Violation: the source never mentions performance,
   but the deck adds a "처리 속도 2배 개선" bullet. This also covers derived
   numbers — recount any total you compute against the source. Violation:
   the source lists 6 skills but the slide claims "총 5개 스킬".
4. **No external dependencies.** Violation:
   `<script src="https://cdn.jsdelivr.net/npm/reveal.js">`. All CSS/JS
   inline, images as relative `assets/` paths, inline SVG, or `data:` URIs —
   the vault is opened offline and CDN links rot.
5. **No translationese.** Not a single sentence may read as awkward to a
   native Korean reader. Violation: "확장하는 것이 가능하다" (write "확장할
   수 있다"), "성능이 천장을 친다" (write "성능이 한계에 부딪힌다").
6. **Delegate saving to the `obs` skill.** Do not re-implement vault paths,
   folder routing, or `Home.md` indexing here. Violation: writing the deck
   directly into `~/workspace/obsidian/MyObsidian/Documents/…` with the
   Write tool instead of calling `Skill(skill="obs", …)`.

---

## Workflow

```
1. Mode detection + interview (AskUserQuestion)  →  2. Source (research | read)
   →  3. Slide outline confirm  →  4. Write slides (Korean)
   →  5. Visuals  →  6. Render deck  →  7. Save via obs  →  8. Report
```

### 1. Mode detection + interview — required, never skip

**Mode** comes from the request itself, not a question: if the user points at
an existing document, vault note, file, or the current conversation's
analysis ("이 문서를", "아까 정리한 내용을") → **conversion mode**; otherwise
→ **new-topic mode**.

Ask in Korean with **one** `AskUserQuestion` call, up to 4 questions. Always
include A and B:

**Question A — slide count** (header: `분량`)

| Option | Description |
|--------|-------------|
| 표준 10~15장 (권장) | 표지 + 목차 + 본론 + 정리. 팀 공유·발표용 기본값 |
| 요약 5~8장 | 핵심만. 짧은 보고·브리핑용 |
| 상세 20장 이상 | 심화 내용·부록 포함. 세미나·교육용 |

**Question B — audience & purpose** (header: `용도`)

- `팀 공유·발표` — 동료 개발자 대상. 결론 중심, 노트에 근거를 담는다.
- `세미나·교육` — 배경지식 없는 청중. 개념을 단계적으로 쌓는다.
- `개인 정리` — 나중에 다시 볼 요약. 노트를 더 상세하게 쓴다.

**Questions C·D — topic-specific (write fresh each time).** Pick the points
that genuinely fork the deck: scope to cover, code examples or not, items
that must appear, emphasis. Mutually exclusive options; put the recommended
one first with `(권장)`.

Restate the answers in one or two Korean sentences and move on.

### 2. Source — research or read, never invent

**New-topic mode** — same discipline as researching a document: list 3–6
claims that must not be guessed (versions, API limits, benchmarks, common
mistakes). Spawn one `Agent` (`subagent_type: "general-purpose"`) per
question, all in one message, `run_in_background: true`, each told to use
WebSearch and answer in 4–6 source-linked bullets. Cross-check surprising
claims against 2+ independent sources. Keep every URL → final sources slide.
Skip research only when the topic is fully known and the user wants a quick
deck — never skip when versions/numbers will appear on slides.

**Conversion mode** — `Read` the source completely before outlining. Every
slide statement must trace back to the source (hard rule 3). If the source
already has good diagrams/data, carry them over; if the source lacks
something the deck seems to need, ask the user instead of inventing it.

### 3. Slide outline — confirm briefly

Present a numbered Korean slide list (`N. 제목 — 한 줄 내용`) and get a nod.
Don't linger. Default skeleton (adapt freely):

```
1. 표지 — 제목 · 부제 · 날짜
2. 목차
3. 문제/배경 — 왜 이 주제인가
4~N. 본론 — 슬라이드당 아이디어 하나
N+1. 정리 — 핵심 요약 3~5개
N+2. 출처 (new-topic mode) / 원문 링크 (conversion mode)
```

### 4. Write slides — concise natural Korean

- **Slide titles are conclusions, not labels.** Good: "캐시 도입으로 응답이
  300ms → 40ms". Bad: "성능 개선".
- Slide body: bullets, numbers, short phrases. Sentence endings (`~다`) are
  fine in notes, avoid them in bullets.
- **Speaker notes per slide: 2–5 sentences of prose** — the explanation you
  would say out loud. This is where the detail from Step 2 lives.
- Example — source paragraph → slide:

  Input (source document): *"기존에는 요청마다 DB를 조회해 평균 응답이
  300ms였다. Redis 캐시를 앞단에 두면서 조회의 92%가 캐시에서 처리되어
  평균 응답이 40ms로 줄었다."*

  Output (slide):
  ```
  제목:  캐시 도입으로 응답 300ms → 40ms
  본문:  • 기존: 요청마다 DB 조회 (평균 300ms)
         • Redis 캐시 도입 후 조회의 92%를 캐시가 처리
  노트:  기존 구조는 모든 요청이 DB까지 내려가 평균 300ms가 걸렸다.
         Redis를 앞단에 두자 조회의 92%가 캐시에서 끝나 평균 응답이
         40ms로 줄었다.
  ```
- Audience level follows Question B. No translationese (hard rule 5); write
  meaning, not word-for-word renderings of English sources.
- The `korean-reviewer` agent attaches automatically via the plugin hook —
  apply its fixes **before saving**.

### 5. Visuals — diagrams where structure lives

Every slide explaining a structure, flow, comparison, or trend gets a
visual. Title, agenda, and summary slides may be text-only. **A deck must
contain at least one visual — conversion mode included**: a text-only source
does not excuse a text-only deck; draw what the text describes. Violation:
converting a README that describes a three-part component structure and a
hook flow into an 8-slide deck with zero diagrams — the structure slide must
be drawn as an SVG.

1. **Inline SVG diagram** — the default. Self-contained, crisp at any scale.
   Read the `svg-visuals` skill before drawing one — it fixes the palette,
   typography, the six layout types, and the Korean label-width math that
   keeps text inside its box.
2. **Inline SVG chart** — for numbers. Read the `dataviz` skill before
   drawing any chart.
3. **Web image** — only clearly reusable ones (official docs assets,
   Wikimedia Commons, Unsplash/Pexels). Download into the deck folder and
   reference relatively — never hotlink:

   ```bash
   curl -L -o "{scratchpad}/{제목}/assets/{파일명}.png" "{이미지 URL}"
   ```

Give every visual a short caption with its source (`출처: 직접 작성` for
your own SVG). If no usable image exists, draw an SVG — never fill the gap
with a copyrighted image.

### 6. Render the deck

Use the template in `references/deck-template.md`. Requirements:

- Complete single file: `<!DOCTYPE html>` … `<html lang="ko">`, all CSS/JS
  inline (hard rule 4)
- 960×540 (16:9) slides, scaled to fit the viewport by inline JS
- Navigation: `←`/`→`, `Space`, `Home`/`End` keys + on-screen `◀`/`▶`
  buttons + `3 / 12` counter; `N` key or `노트` button toggles the speaker
  notes panel
- Print stylesheet: one slide per page with its notes below — the deck
  doubles as a PDF handout
- Light minimal design: white slides, one accent color, `word-break: keep-all`

Write to `{scratchpad}/{제목}/index.html` (+ `assets/` if needed) first.

### 7. Save — delegate to `obs`

Call the **`obs`** skill via the `Skill` tool with a folder hint and title,
saving `index.html` (and `assets/`) as attachments:

```
Skill(skill="obs", args='Documents/ "{제목}"')
```

- Folder routing follows `obs` rules; omit the hint when unsure. (발표자료·
  개념 정리 → `Documents/`, 기술 조사 발표 → `Research/`, 특정 프로젝트
  발표 → `Projects/`)
- The folder-note `.md` must be created with: a 3–5 line Korean summary,
  the slide list from Step 3, and an `[[index.html]]` link.
- `obs` updates the `Home.md` index.

### 8. Report — in Korean

```
✓ 슬라이드 덱을 만들어 Obsidian에 저장했습니다.
  경로: Documents/{제목}/index.html
  노트: Documents/{제목}/{제목}.md
  구성: 슬라이드 {N}장 · 그림 {M}개 · 발표자 노트 포함
  조작: ←/→ 넘김 · N 키 발표자 노트 · 인쇄하면 PDF 유인물
  열기: obsidian://open?vault={vault 이름}&file={URL인코딩된 경로}
```

---

## Style

- Interview and outline confirmation are **fast**; research, writing, and
  drawing proceed autonomously without pinging the user per slide.
- Talk to the user in Korean from start to finish.
