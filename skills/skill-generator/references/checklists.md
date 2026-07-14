# Verification Checklists

Run BOTH gates on every generated or improved skill. Fix and re-check on any
failure — never deliver with an open item.

## Gate 1 — Pre-launch checklist

Frontmatter:
- [ ] Frontmatter contains valid `name` and `description` (plus only
      intentional extensions like `allowed-tools`).
- [ ] `name` ≤64 chars; lowercase/numbers/hyphens only; no reserved words
      ("anthropic", "claude").
- [ ] `description` ≤1024 chars, third person, states both function and
      use case.

Body:
- [ ] Body under 500 lines.
- [ ] Supplementary files linked at depth 1 only (SKILL.md → file, no chains).
- [ ] At least one concrete input→output example.
- [ ] One default per decision point — no "use A, B, or C" without a default.
- [ ] No time-locked language ("until <date>…") without a versioning strategy.
- [ ] All file paths use forward slashes.
- [ ] MCP tools referenced as `server:tool`.

Resources (when present):
- [ ] Scripts handle their own errors (validate inputs, exit non-zero with a
      clear message) — nothing punted to the agent.
- [ ] Every references/ file is actually pointed to from SKILL.md.

## Gate 2 — Description quality checklist

- [ ] Specific keywords included: file types, operations, domain terms.
- [ ] Contains the user's literal trigger phrases (Korean ones verbatim when
      the user triggers in Korean).
- [ ] States what the skill *enables*, not what it *is*.
- [ ] No first person ("I can…").
- [ ] Includes explicit "use when…" trigger framing.

## Gate 3 — Trigger-matching test

The agent selects skills from descriptions **alone** — so test the
description alone.

1. Write **3 representative requests** — realistic phrasings the user would
   actually type (reuse interview answers; vary wording, don't just copy the
   trigger phrases).
2. Write **1 near-miss request** — plausibly adjacent but should NOT trigger
   this skill (e.g. for a commit-message skill: "explain what this diff
   does").
3. For each of the 4, judge: reading *only* this skill's description next to
   the descriptions of the user's other installed skills, would the agent
   pick this skill?
   - Representative requests: all 3 must select it.
   - Near-miss: must NOT select it.
4. On any failure, revise the description (add missing keywords, sharpen the
   "use when" boundary, add an exclusion) and re-run all 4.

Report format (include in the final user-facing report, in Korean):

| # | 요청 | 기대 | 판정 |
|---|------|------|------|
| 1 | "…" | 발동 | ✅ |
| 2 | "…" | 발동 | ✅ |
| 3 | "…" | 발동 | ✅ |
| 4 | "…" (near-miss) | 미발동 | ✅ |
