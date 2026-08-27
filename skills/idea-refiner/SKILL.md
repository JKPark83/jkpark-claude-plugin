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

1. **Restate the seed and size it.** In one Korean sentence, reflect the idea
   back so the user confirms you understood it. Then say out loud how big you
   read it as — **작은 기능** (converges in 2–3 batches) vs **독립 프로젝트**
   (needs the whole checklist) — so the user can correct you. When torn, take
   the heavier read.
   **Decomposition guard:** if the seed is really several independent pieces
   ("채팅 + 결제 + 분석 대시보드"), stop and split it first, then ask which
   piece to spec now. Never spend questions detailing a project that should
   have been decomposed.
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
   if the user explicitly says it's out of scope — or, on the **작은 기능**
   path, if it plainly doesn't apply (say which ones you're skipping and why).
5. **Offer options when the user is stuck.** If they hesitate, propose 2–3
   concrete choices to react to instead of asking them to invent an answer.
6. **Converge and summarize** the moment the convergence test passes — don't
   keep asking once the idea is buildable.

## Checklist — dimensions to pin down

- **Problem & target user** — who hurts, how, and which *one* primary user
  (a concrete person, not a segment). Always ask for **근거**: 본인 경험, 주변
  사례, 경쟁 서비스 리뷰, 검색 데이터. 근거가 없으면 그건 문제가 아니라 가정이다.
- **Goal & success metric** — three kinds, each with a number:
  - **핵심 지표** — the ONE number this must move (현재값 → 목표값 → 언제 측정).
  - **보조 지표** — watched, not optimized for.
  - **가드레일 지표** — what must NOT get worse. Every idea has a side effect;
    if the user can't name one, the trade-off hasn't been thought through.
- **MVP scope** — smallest shippable version. For every excluded item get the
  **이유** ("나중에"는 이유가 아니다) and whether it's a later phase.
- **Core user flow** — the main journey, step by step.
- **Tech approach** — stack, services, data model, integrations. Where there's
  a real fork, lay 2–3 options side by side with trade-offs and **lead with
  your recommendation** rather than making the user invent one.
- **Constraints** — time, budget, platform, team, compliance.
- **Risks & open questions** — top 2–3 things that could sink it, each with a
  concrete mitigation. "잘 지켜보자"는 완화책이 아니다.

Every feature must trace back to a problem on this list. One that answers no
stated problem is scope creep — move it to 제외 or drop it.

## Tag every gap: 🔶 가정 / 🔵 오픈 질문

Never invent a number, a user behavior, or a technical fact to fill a hole.
Tag it inline the moment it appears, and carry the tag into the summary:

- **🔶 가정** — you inferred it; plausible but unvalidated.
  *(예: "🔶 가정: 주 사용자는 하루 1회 이상 앱을 연다 — 유사 서비스 기준 추정, 미검증")*
- **🔵 오픈 질문** — unknown; needs discovery, a decision, or data you don't have.
  *(예: "🔵 오픈 질문: 무료 티어 API 호출 한도 확인 필요")*

An untagged 🔶 is the most common way a spec turns out wrong. A 🔶 that would
sink the idea if false belongs in 리스크 as well.

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

- one-sentence **problem** (who hurts + how) **with 근거 behind it**,
- a **specific primary user** (not "everyone"),
- a **핵심 지표** with 현재값 → 목표값,
- the **MVP scope** with what's in and what's out — and *why* it's out,
- the **core flow** as ordered steps,
- a **tech approach** concrete enough to start coding,
- the **first 3–5 implementation tasks**,
- the top **2–3 risks**, each with a mitigation.

Then run one consistency pass before writing the summary:

- Does every 포함 feature trace to the stated problem?
- Does the 핵심 지표 actually measure *that* problem? (문제가 "뭘 먼저 할지
  모른다"인데 지표가 "페이지뷰"면 어긋난 것이다.)
- Does 제외 contradict 포함, or quietly drop something the user expects to get?
- Any leftover "TBD", placeholder, or requirement readable two ways? Pick one
  reading and make it explicit.

Fix mismatches inline. If anything would still read as vague, ask another
batch. Don't stop early.

## Output

When converged, **print this summary to screen by default**, in Korean Markdown:

```markdown
# 💡 <아이디어 이름>

## 한 줄 요약
<[사용자]를 위해 [문제]를 해결하는 [솔루션]. 성공하면 [측정 가능한 결과].
 한 문장에 안 들어가면 범위가 아직 안 좁혀진 것이다.>

## 문제 / 타겟 사용자
<누가 · 무엇이 · 왜 아픈가 + 근거(있으면 출처, 없으면 🔶 태그)>

## 목표 & 성공 지표
| 구분 | 지표 | 현재 | 목표 | 측정 시점 |
|---|---|---|---|---|
| 핵심 | | | | |
| 보조 | | | | |
| 가드레일 | <나빠지면 안 되는 것> | | <이 선은 지킨다> | |

## MVP 범위
**포함** — <각 항목이 위 문제 중 무엇을 푸는지>
**제외** — <항목 + 왜 지금은 아닌지 + 나중에 볼지 여부>

## 핵심 사용자 플로우
## 기술 접근
<선택안 + 탈락시킨 대안과 그 이유>

## 첫 구현 단계 (3~5개)
## 리스크 & 오픈 질문
<리스크는 각각 완화책까지. 본문에 붙은 🔶 가정 / 🔵 오픈 질문을 여기 모은다.>

## 자체 점검
- **가장 약한 부분**: <어느 섹션이 제일 근거가 얇은지, 왜>
- **반드시 검증할 가정 3개**: <🔶 중 틀리면 제일 크게 무너지는 것 + 검증 방법>
- **다음 한 걸음**: <만들기 전에 해야 할 단 하나의 행동>

## 참고 자료   ← only when web research was done; include the source links
```

Leave a table row or a bullet empty rather than inventing a plausible number.
An empty cell is a visible gap; a made-up one is a silent bug.

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
