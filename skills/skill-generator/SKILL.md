---
name: skill-generator
description: >-
  Use when the user wants to create a new Claude Code skill (SKILL.md) or
  audit/improve an existing one. Triggers on "스킬 만들어줘", "새 스킬 생성해줘",
  "SKILL.md 작성해줘", "이 작업을 스킬로 만들어줘", "스킬 점검해줘", "스킬 개선해줘",
  "create a skill", "generate a skill", "audit this skill", "skill-generator",
  or "/skill-generator". Always interviews the user first (AskUserQuestion) to
  pin down purpose, triggers, autonomy, and tool dependencies, then generates
  an English SKILL.md following progressive-disclosure best practices, verifies
  it against a pre-launch checklist, a trigger-matching test, and a behavioral
  evaluation on real sample inputs, and asks where
  to save it (personal, project, or the jkpark-claude-plugin repo — updating
  plugin.json when saving there).
---

# Skill Generator

Create high-quality Claude Code skills — or audit and improve existing ones —
following the SKILL.md open standard and progressive-disclosure methodology.

**Language rules:**
- This skill file and **every generated SKILL.md are written in English.**
  Korean trigger phrases MAY appear inside the generated `description` when the
  user's typical requests are in Korean (see the description guide).
- **All conversation with the user — interview questions, findings, reports —
  is in Korean (한국어).**

## Hard rules

1. **Never generate without the interview.** Requirements come from the user,
   not from guesses (Step 1).
2. **Description first.** The description does 80% of the work — draft and
   polish it before writing the body.
3. **Never deliver unverified.** Every generated or improved skill must pass
   the pre-launch checklist, the trigger-matching test, AND the behavioral
   evaluation (Step 5) — a skill that has never produced an output is not done.
4. **Never commit.** Create/edit files only. When the destination is a git
   repo (plugin or project), remind the user at the end to commit themselves
   (e.g. via the `/commit` skill); a personal save (`~/.claude/skills/`) needs
   no commit reminder.

## Mode detection

- User describes a task to package, or asks for a new skill → **Create mode**.
- User points at an existing skill/SKILL.md and asks to check, fix, or improve
  it → **Improve mode** (see "Improve mode" below).

Before either mode, **read `references/best-practices.md` and
`references/checklists.md`** — all principles, anti-patterns, and checklists
live there.

---

## Create mode

```
1. Interview  →  2. Save location  →  3. Description draft
→  4. Body + scaffolding  →  5. Verify (checklist + matching + behavioral eval)
→  6. Register (plugin.json)  →  7. Report
```

### 1. Interview — required, never skip

Ask in Korean with `AskUserQuestion`, batching up to 4 questions per call.
Cover all four dimensions (split into two calls if options need depth):

| Dimension | What to pin down |
|-----------|------------------|
| **Purpose & triggers** | The repetitive task the skill packages; the exact situations/phrases that should activate it; what is explicitly out of scope. |
| **Autonomy level** | Free-form guideline (open-ended work like reviews) vs. strict ordered procedure (order-sensitive work like migrations). |
| **Tools & dependencies** | MCP tools (`server:tool` notation), external CLIs, other skills to delegate to, whether `allowed-tools` is needed. |
| **Real samples & I/O** | At least one concrete input → output example. When the skill produces artifacts the user already creates (commit messages, Jira tickets, reports, docs), collect 2–3 real past samples — ask for them, or fetch them directly with available tools (git log, Jira API, vault search). Derive template/format options from those samples instead of inventing them, and keep the samples as holdout inputs for the behavioral evaluation (Step 5). |

If the user's initial message already answers a dimension clearly, don't
re-ask it — confirm it in one Korean sentence instead. After the interview,
restate the full requirement in 2–3 Korean sentences and get a nod.

### 2. Save location — ask every time

One `AskUserQuestion` (header: `저장 위치`):

| Option | Path | Notes |
|--------|------|-------|
| Personal | `~/.claude/skills/<name>/` | All projects, this machine only. |
| Project | `<repo>/.claude/skills/<name>/` | This project only, git-sharable. |
| Plugin | `jkpark-claude-plugin/skills/<name>/` | Personal plugin; triggers Step 6. |

### 3. Description draft — the 80% step

Draft the frontmatter `description` before anything else, then run it through
the **Description Quality Checklist** in `references/checklists.md`. Iterate
until every item passes. Requirements: third person, states what + when, ≤1024
chars, concrete trigger keywords (include the user's literal Korean phrases
when they trigger in Korean).

`name`: lowercase/numbers/hyphens only, ≤64 chars, no reserved words
("anthropic", "claude").

### 4. Body + scaffolding

Write the body applying `references/best-practices.md`. Key constraints:

- **≤500 lines**, frequent operations inline, example-driven (input→output
  pairs beat prose).
- **Progressive disclosure**: move long reference material to
  `references/*.md`, linked **one level deep only**.
- **Scripts** (`scripts/*.py` etc.) only for deterministic operations
  (validation, transformation), with internal error handling — never push
  debugging onto the agent.
- Match autonomy to the interview answer: checklist-style freedom vs.
  numbered strict procedure.
- One default per decision point — never "use A, B, or C".
- Forward slashes in all paths; no time-locked rules.

### 5. Verify — checklist + matching + behavioral eval

Run the three delivery gates from `references/checklists.md`:

1. **Pre-launch checklist** (Gate 1) — every item, mechanically. Fix and
   re-check on any failure.
2. **Trigger-matching test** (Gate 3) — write 3 representative user requests
   + 1 near-miss that must NOT trigger. Judge each against the description
   *alone* (that is all the agent sees at selection time), alongside the
   descriptions of the user's other installed skills to catch overlap. If any
   representative request would miss, or the near-miss would fire, revise the
   description and re-test.
3. **Behavioral evaluation** (Gate 4) — static checks prove the skill
   activates; only execution proves it behaves. Run 1–3 sample inputs
   (prefer the real samples collected in the interview) through fresh
   subagents that see only the generated skill body plus the input, then
   judge each output per Gate 4. On any violation, fix the body and re-run
   that case.

Show the matching-test table (request → expected → verdict) and the
behavioral-eval table (case → violation → resolution) in the final report.

### 6. Register — plugin destination only

When saved into `jkpark-claude-plugin`:

- `.claude-plugin/plugin.json`: append the skill to `description`, add
  relevant `keywords`, bump minor version (e.g. 0.4.0 → 0.5.0).
- `.claude-plugin/marketplace.json`: sync `metadata.version`.

Skip this step entirely for personal/project destinations.

### 7. Report — in Korean

```
✓ 스킬 '{name}'을(를) 생성했습니다.
  경로: {SKILL.md path}
  구조: SKILL.md ({N}줄) + references/ {M}개 + scripts/ {K}개
  검증: 체크리스트 통과 · 매칭 테스트 {3}/3 + 오발동 방지 확인
        · 행동 평가 {K}건 통과 ({위반·수정 내역 한 줄, 없으면 "위반 없음"})
  {plugin.json 갱신 내역 — 플러그인 저장 시}
  {커밋 안내 — 플러그인/프로젝트 저장 시에만: "커밋은 직접 진행해주세요 (/commit 사용 가능)"}
```

After saving, check the session's available-skills list: new skills usually
register immediately. Only if the skill is not listed there, tell the user
to restart the session.

---

## Improve mode

1. **Read** the target SKILL.md (and its references/scripts). If the user
   didn't give a path, locate it under `~/.claude/skills/`, `.claude/skills/`,
   or the plugin's `skills/`.
2. **Audit** against both checklists in `references/checklists.md` plus the
   anti-pattern list in `references/best-practices.md`.
3. **Report findings in Korean** as a table: item → current state → problem →
   proposed fix, ordered by impact (description issues first — they block
   activation entirely).
4. **Apply fixes.** If any fix changes the skill's behavior or trigger scope
   (not just format), confirm those with `AskUserQuestion` first; apply pure
   format/compliance fixes directly.
5. **Re-verify** with all three delivery gates — include a behavioral re-run
   (Gate 4) whenever a fix touched output rules or templates — then report as
   in Create Step 7.

---

## Style

- Interview fast, generate autonomously — don't ping the user between Steps
  3–5 unless a requirement is genuinely ambiguous.
- Keep generated skills lean: assume the model is smart, skip foundational
  explanations, cut anything the checklist doesn't require.
- When improving, preserve the original author's structure and voice unless
  it violates a checklist item.
