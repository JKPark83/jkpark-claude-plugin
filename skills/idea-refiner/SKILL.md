---
name: idea-refiner
description: >-
  Use when the user wants to brainstorm, flesh out, pressure-test, or scope a
  new idea, feature, product, or project — including openers like "이런 기능
  어떨까?", "새 아이디어가 있어", "이거 한번 만들어볼까?", "이 방향 어때?",
  "이거 기획 좀 같이 해줘", "let's think through this feature", or "help me
  spec this out". Drives an iterative Korean Q&A that drills a vague concept
  down to a concrete, immediately buildable spec, runs parallel web research
  when external facts are needed, then prints a structured summary on screen
  and can optionally save it as a Markdown file.
---

# Idea Refiner

Turn a half-formed idea into a concrete, immediately-actionable spec by asking
the user sharp, sequential questions — one small batch at a time — until every
dimension needed to start building is nailed down.

**Language rule:** This skill file is written in English, but **every question
you ask the user and the final summary MUST be in Korean (한국어).** The user
thinks and answers in Korean. Internal reasoning can be in any language.

## How to run it

1. **Restate the seed.** In one Korean sentence, reflect the idea back so the
   user confirms you understood it correctly. Then start questioning.
2. **Ask in small batches.** 1–3 focused questions per turn — never a wall of
   them. Each batch targets the *single most uncertain* part of the idea right
   now. Prefer concrete, decision-forcing questions over open ones:
   - 약함: "사용자는 누구인가요?"
   - 강함: "주 사용자는 '매일 쓰는 헤비 유저'인가요, '가끔 들르는 신규
     방문자'인가요? 딱 하나만 고른다면요?"
3. **Drill vague answers.** If an answer stays abstract ("빠르면 좋겠어요"),
   immediately ask a quantifying follow-up ("응답이 몇 초 안에 떠야 '빠르다'고
   느끼실까요?"). Never let a fuzzy answer pass.
4. **Cover every dimension** in the Checklist before converging. Skip one only
   if the user explicitly says it's out of scope.
5. **Offer options when the user is stuck.** If they hesitate, propose 2–3
   concrete choices to react to instead of asking them to invent an answer.
6. **Converge and summarize** the moment the convergence test passes — don't
   keep asking once the idea is buildable.

## Checklist — dimensions to pin down

- **Problem & target user** — who hurts, how, and which *one* primary user.
- **Goal & success metric** — what "it worked" looks like, measurably.
- **MVP scope** — smallest shippable version; what is explicitly *out*.
- **Core user flow** — the main journey, step by step.
- **Tech approach** — stack, services, data model, integrations.
- **Constraints** — time, budget, platform, team, compliance.
- **Risks & open questions** — top 2–3 things that could sink it.

## Parallel web research (do NOT block the conversation)

Whenever an answer depends on an external fact you should not guess — a
competing product, an API's limits, a pricing model, a library's capability, a
market norm, a regulation — launch web research as **background subagents** and
keep talking instead of stalling:

- Use the **Agent** tool with `subagent_type: "general-purpose"`, **one agent
  per distinct question**, and put them **all in a single message so they run
  in parallel**. Set `run_in_background: true` so the Q&A continues.
- Give each agent a tight prompt: the exact question + "Use WebSearch for the
  latest sources. Return 3–5 bullet findings, each with a source link."
- When results arrive, fold them into your next batch ("찾아보니 경쟁 서비스
  X는 무료 티어가 없네요 — 그래도 무료 플랜으로 갈까요?").

Trigger research the instant you notice yourself about to assume a number, a
competitor's behavior, or whether something is technically feasible.

## Convergence test — stop asking when ALL are true

You can now write, concretely and without hand-waving:

- one-sentence **problem** (who hurts + how),
- a **specific primary user** (not "everyone"),
- the **MVP scope** with what's in and what's out,
- the **core flow** as ordered steps,
- a **tech approach** concrete enough to start coding,
- the **first 3–5 implementation tasks**,
- the top **2–3 risks**.

If any of these would still read as vague, ask another batch. Don't stop early.

## Output

When converged, **print this summary to screen by default**, in Korean Markdown:

```markdown
# 💡 <아이디어 이름>

## 한 줄 요약
## 문제 / 타겟 사용자
## 목표 & 성공 지표
## MVP 범위 (포함 / 제외)
## 핵심 사용자 플로우
## 기술 접근
## 첫 구현 단계 (3~5개)
## 리스크 & 오픈 질문
## 참고 자료   ← only when web research was done; include the source links
```

Then ask in Korean: **"이 내용을 마크다운 파일로 저장할까요?"**

- **Yes →** write it to `./ideas/<slug>-<YYYY-MM-DD>.md` (create `ideas/` if it
  doesn't exist; `<slug>` is a short kebab-case name; use the date from the
  session context), then confirm the saved path.
- **No →** leave it on screen only.

## Style

- One batch of questions per turn; wait for the answer before the next batch.
- Mirror the user's words; guide, don't lecture.
- Every turn must make the idea more concrete than the turn before it.
- Keep it conversational — this is a working session, not an interrogation.
