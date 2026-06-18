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

## Repository layout

```
.claude-plugin/
  plugin.json        # plugin manifest
  marketplace.json   # marketplace entry (lets you install this repo locally)
skills/
  idea-refiner/
    SKILL.md         # the skill (English instructions, Korean Q&A)
  tech-blog-writer/
    SKILL.md         # the skill (English instructions, Korean output)
    references/
      translation-and-style.md   # natural EN→KO translation + junior-audience guide
      html-templates.md          # standalone + CMS-fragment HTML templates
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
