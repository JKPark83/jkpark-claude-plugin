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

## Repository layout

```
.claude-plugin/
  plugin.json        # plugin manifest
  marketplace.json   # marketplace entry (lets you install this repo locally)
skills/
  idea-refiner/
    SKILL.md         # the skill (English instructions, Korean Q&A)
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
