# Verification Checklists

Run every gate on each generated or improved skill (Gate 2 runs during
description drafting; Gates 1, 3, and 4 are the delivery gates). Fix and
re-check on any failure — never deliver with an open item.

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
- [ ] Every behavioral rule ("never X", "always Y") is paired with one
      concrete violation example marking the boundary.
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

## Gate 4 — Behavioral evaluation

Static checks prove the skill is well-formed and will activate; only
execution proves it behaves. Never deliver a skill that has not produced at
least one output.

1. Prepare 1–3 sample inputs. Prefer real past artifacts collected in the
   interview (actual tickets, commits, reports); the body must not have been
   written against those exact samples.
2. For each input, run a fresh subagent that sees ONLY the generated skill
   body plus the input (never the expected output), and have it produce the
   skill's output.
3. Judge each output against:
   - the skill's own rules — especially fact fidelity: nothing in the output
     that is not in the input or a necessary consequence of it;
   - the template — all sections present, in order, correctly used;
   - the real artifact, when one exists — facts dropped? structure lost?
4. Any violation (invented content, missing sections, unverifiable
   completion criteria) → fix the skill body — usually by adding a violation
   example to the offending rule — then re-run that case.

Report format (include in the final user-facing report, in Korean):

| # | 입력 사례 | 위반 | 조치 |
|---|-----------|------|------|
| 1 | "…" | 없음 | — |
| 2 | "…" | 작업 항목 창작 1건 | 규칙에 위반 예시 추가 → 재실행 통과 |
