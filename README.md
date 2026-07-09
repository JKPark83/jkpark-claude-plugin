# jkpark-claude-plugin

A personal [Claude Code](https://docs.claude.com/en/docs/claude-code) plugin.

## Skills

### `idea-refiner`

An iterative **Korean Q&A** session that turns a vague idea or feature into a
concrete, immediately-buildable spec. It asks sharp, decision-forcing questions
one small batch at a time, runs **parallel web research** as background
subagents when external facts are needed, and finally prints a structured
summary on screen — which you can optionally save as a Markdown file under
`ideas/`.

It auto-triggers when you open with things like:

> "이런 기능 어떨까?" · "새 아이디어가 있어" · "이거 한번 만들어볼까?"

Or invoke it explicitly with `/idea-refiner`.

### `tech-blog-writer`

Turns a **topic or a source article (URL)** into a finished **technical blog
post** — researched, written for a **junior developer**, **image-rich** (it
searches the web for relevant visuals and embeds them with attribution),
**naturally translated** from English sources into Korean (no 번역투), and
rendered as **HTML**. When done it asks **where to publish**, **remembers** your
frequent targets, and offers to reuse them next time — supporting both **GitHub
Pages / static repos** (write file + `git commit`/`push`) and **CMS paste**
(Tistory / Velog / WordPress).

It auto-triggers when you say things like:

> "이 주제로 기술 블로그 써줘" · "이 링크 글로 정리해줘" · "이거 블로그 글로 써줘"

Or invoke it explicitly with `/tech-blog-writer`.

Remembered publish targets are stored at `~/.claude/blog-writer/targets.json`.

### `obs` / `obs-recall`

The **write** and **read** halves of an Obsidian vault used as a personal
knowledge base.

- **`obs`** saves content — Claude's last reply, a note, analysis artifacts —
  into the vault as a **folder-note** (`{폴더}/{제목}/{제목}.md`) with
  frontmatter tags, auto-routing by topic into `Projects/` · `Documents/` ·
  `Paper/` · `Research/` · `Inbox/`, bundling any attachments (HTML, images)
  alongside the note, and updating the `Home.md` index. It reuses tags already
  present in the vault so the tag set doesn't sprawl.
- **`obs-recall`** searches the vault — index → frontmatter tags → full text, in
  that order (cheapest first). It knows the real content often lives in an
  attached HTML file rather than the `.md`, so it searches and text-extracts
  those too, and it always cites the source note's vault path. Read-only.

Trigger them with `/obs`, `/obs-recall`, or naturally:

> "이거 볼트에 저장해줘" · "예전에 정리한 거 있나?" · "볼트에서 찾아봐"

> **Vault location:** both read `$OBSIDIAN_VAULT`, falling back to
> `~/workspace/obsidian/MyObsidian`. Set the env var if your vault lives
> elsewhere.

### `obs-html`

Writes a topic up as a **self-contained, image-rich Korean HTML document** and
files it into your **Obsidian vault**. It always **interviews you first** (via
`AskUserQuestion`) to pin down the **total length** and whether this is a
**technical** or **non-technical** document, plus whatever else the topic
genuinely hinges on. Technical docs are pitched so a **junior developer** can
follow them; everything else is explained in plain language. The Korean reads
naturally (no 번역투), and **every major section carries a visual** — a
hand-drawn inline SVG diagram by default, or a properly attributed web image
downloaded into the note's `assets/`. The HTML has **zero external
dependencies** (no CDN, no web fonts) so it still opens years from now, offline.
Saving is delegated to the `obs` skill, which files it as a folder-note and
updates `Home.md`.

It auto-triggers when you say things like:

> "이 주제로 HTML 문서 만들어서 obs에 저장해줘" · "HTML로 정리해서 볼트에 넣어줘"

Or invoke it explicitly with `/obs-html`.

> Requires the `obs` skill (Obsidian vault saving) to be available.

### `analyze-image`

Looks at an image you want analyzed **without making you mention the
clipboard**. When you ask Claude to look at / read / explain / debug an image,
screenshot, screen, UI, error, or diagram — and you didn't attach a file or
give a path — the picture is almost always on the macOS **clipboard** (you just
hit ⌘⇧4 / ⌃⌘⇧4 or copied an image). So this skill **checks the clipboard first
by default**, pulls whatever screenshot/picture is there into a temp PNG via
`osascript`, reads it, and answers in Korean. If the clipboard is empty it asks
you to capture/copy/attach an image or give a path.

It auto-triggers when you say things like:

> "이 이미지 분석해줘" · "이 화면 뭔지 봐줘" · "방금 캡쳐한 거 봐바" · "이 에러 화면 분석해줘"

Or invoke it explicitly with `/analyze-image`.

> macOS only (uses `osascript`; no extra install). The clipboard image is
> dumped to a single fixed temp file that's overwritten on each run.

## Agents

### `korean-reviewer`

A **Sonnet**-backed subagent that proofreads a finished **Korean document**
(Markdown / HTML / PPTX text) for **unnatural Korean** and rewrites it into
natural, idiomatic phrasing — catching 번역투, English-calque wording, stiff
officialese, and mistranslated idioms (e.g. "천장을 친다" → "한계에 부딪힌다").
It preserves meaning, structure, code, and proper nouns, fixes only what is
clearly unnatural, and returns a concise table of every change.

## Hooks

A **`PostToolUse`** hook watches `Write` / `Edit` / `MultiEdit`. Right after a
**reader-facing document** (`.md` / `.html` / `.pptx`) is written, it advises
the main session to run the `korean-reviewer` agent on that file. It's
**advisory only** (never blocks), skips the plugin's own internal files, and —
when several documents are produced at once — authorizes reviewing them **in
parallel**. So generated Korean documents get proofread automatically.

## Status line (opt-in)

An **animated emoji status line** lives under [`statusline/`](statusline/). The
mascot reacts to Claude's state — **🤖↔🧠 (orange)** while Claude is working,
**😴↔💤 (blue)** while idle — and the line also shows
`dir | git | model | effort | context%`.

Claude Code plugins **cannot** register a main `statusLine` (only your own
`settings.json` can), so this is a **copy-in** extra rather than an
auto-activated plugin feature: drop `statusline/claude-statusline.sh` into
`~/.claude/`, merge `statusline/settings-snippet.json` into your
`settings.json`, and restart. Full instructions and customization are in
[`statusline/README.md`](statusline/README.md).

## Repository layout

```
.claude-plugin/
  plugin.json        # plugin manifest (references hooks/hooks.json)
  marketplace.json   # marketplace entry (lets you install this repo locally)
skills/
  idea-refiner/
    SKILL.md         # the skill (English instructions, Korean Q&A)
  tech-blog-writer/
    SKILL.md         # the skill (English instructions, Korean output)
    references/
      translation-and-style.md   # natural EN→KO translation + junior-audience guide
      html-templates.md          # standalone + CMS-fragment HTML templates
  obs/
    SKILL.md         # save content into the Obsidian vault as a tagged folder-note
  obs-recall/
    SKILL.md         # search the vault (index → tags → full text, incl. attached HTML)
  obs-html/
    SKILL.md         # interview → research → Korean HTML doc → save via the obs skill
    references/
      writing-style.md   # 번역투 blacklist + junior / non-technical audience rules
      html-template.md   # dependency-free, light+dark HTML template & SVG figure recipes
  analyze-image/
    SKILL.md         # checks the macOS clipboard first when asked to analyze an image
    grab-clipboard.sh # osascript: dump clipboard image → temp PNG (or ERR_NO_IMAGE)
agents/
  korean-reviewer.md # Sonnet proofreader for unnatural Korean in generated docs
hooks/
  hooks.json         # PostToolUse → suggest korean-reviewer after doc writes
  scripts/
    korean-doc-check.sh   # detects .md/.html/.pptx writes, emits the advisory
statusline/
  claude-statusline.sh    # opt-in animated status line (working 🤖🧠 / idle 😴💤)
  settings-snippet.json   # statusLine + hooks block to merge into settings.json
  README.md               # install + customization guide
README.md
```

## Try it locally

This repo doubles as its own Claude Code marketplace, so you can install it
from disk:

```bash
# inside Claude Code, from this repo:
/plugin marketplace add ./
/plugin install jkpark-claude-plugin@jkpark-plugins
```

Then start a session and say "이런 기능 어떨까? …" — the `idea-refiner` skill
should load automatically. Or run `/idea-refiner` directly.

## Publish

Push this repo to GitHub, then anyone can install it with:

```bash
/plugin marketplace add <your-org>/jkpark-claude-plugin
/plugin install jkpark-claude-plugin@jkpark-plugins
```
