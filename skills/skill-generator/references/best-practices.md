# SKILL.md Best Practices

Distilled from Anthropic's Agent Skills guidance and the SKILL.md open
standard (Linux Foundation Agentic AI Foundation; read by 30+ tools including
Claude Code, Codex CLI, Gemini CLI, Cursor).

## Core concept: progressive disclosure

Knowledge loads in three stages — keep each stage as small as it can be:

| Stage | When loaded | Token cost | Content |
|-------|-------------|-----------|---------|
| Metadata | Always (session start) | ~100 tokens/skill | `name` + `description` |
| Body | When matched to a request | <5k tokens | SKILL.md markdown body |
| Resources | On demand | Zero if unused | references/, scripts/ |

Consequence: the description carries the entire activation decision; the body
carries only what is needed on *most* invocations; everything else goes to
resource files.

## Directory layout

```
skill-name/
├── SKILL.md          # required: frontmatter + instructions
├── references/       # optional: detailed guides, API/reference docs
│   └── *.md
└── scripts/          # optional: executable helpers
    └── *.py
```

## Frontmatter spec

- `name` — required; ≤64 chars; lowercase letters, numbers, hyphens only;
  must not contain reserved words ("anthropic", "claude").
- `description` — required; ≤1024 chars; third person; states **what it does
  AND when to use it** with concrete keywords.
- Claude Code extensions (use only when needed):
  - `allowed-tools` — auto-permit specific tools.
  - `disable-model-invocation: true` — slash-command-only skills.

## Writing the description

The agent chooses skills based **solely on this field** — it does 80% of the
work.

- State what the skill *enables*, not what it *is*.
- Include concrete trigger keywords: file types, operations, domain terms,
  and the user's literal phrases (Korean phrases included when the user
  triggers in Korean).
- Third person; never "I can…".
- Good: *"Analyzes Excel files, creates pivot tables and charts. Use for
  spreadsheet/xlsx/tabular data."*
- Bad: *"A helpful skill for working with data files."*

## Content organization

- Body **under 500 lines**; put frequently-used content inline, link the rest.
- **One-level-deep linking only** — never SKILL.md → advanced.md →
  details.md; agents skip intermediate hops.
- Example-driven: concrete input→output pairs beat paragraphs of explanation.
- Assume the model is smart — skip foundational definitions.
- Tailor autonomy to the task:
  - High freedom (guidelines, checklists) for open-ended work — code review,
    writing.
  - Tight numbered procedures for order-dependent work — database migration,
    release steps.
- Scripts are for **deterministic** operations (validation, transformation):
  they run identically every time, whereas generated code must be re-derived
  each invocation. Scripts must handle their own errors — never delegate
  debugging to the agent.
- Externalize time-sensitive info (versions, deprecations) into references or
  clearly versioned sections.
- Reference MCP tools as `server:tool` (e.g. `BigQuery:bigquery_schema`).
  MCP provides capability (what you can do); skills teach methodology (how).

## Anti-patterns

| Anti-pattern | Why it fails |
|--------------|-------------|
| Weak/vague description | Skill never activates — the #1 failure mode. |
| Bloated body, long prerequisites | Buries the core procedure. |
| Deep file nesting | Agents skip intermediate files. |
| "Use A, B, or C…" without a default | Confuses the model; pick one, document exceptions. |
| Windows path syntax (`scripts\file.py`) | Breaks cross-platform; always forward slashes. |
| Scripts that punt errors to the agent | Turns a deterministic step into a debugging session. |
| Time-locked rules ("until August 2025 use old API") | Becomes stale documentation. |
| Shipping unvetted third-party skills | Skills are software — inspect before installing. |

## Scope reference

| Scope | Path | Applies to |
|-------|------|-----------|
| Personal | `~/.claude/skills/<name>/SKILL.md` | All projects on this machine |
| Project | `<repo>/.claude/skills/<name>/SKILL.md` | That project only; git-sharable |
| Plugin | `<plugin>/skills/<name>/SKILL.md` | Wherever the plugin is installed |

## Worked example

```yaml
---
name: writing-commits
description: Analyzes git diff and writes messages matching team convention.
  Use when committing code changes.
---

# Commit Message Writing

Format: `type(scope): summary` + blank line + details.
Types: feat, fix, chore, docs, refactor, test.

## Examples

Input: Add JWT token login authentication
Output:
    feat(auth): Implement JWT-based authentication

    Adds login endpoint and token validation middleware.

## Rules

- Summary ≤50 chars, imperative mood
- Explain what and why; let code explain how
```

Note what makes it work: tiny body, one format with no alternatives, a
concrete input→output pair, and a description that names both the action
("analyzes git diff and writes messages") and the trigger ("when committing").
