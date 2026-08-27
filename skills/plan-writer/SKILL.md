---
name: plan-writer
description: >-
  Use when the user has an idea spec / 기획서 (typically produced by
  idea-refiner) and wants it turned into a very detailed, code-level
  implementation plan document — openers like "상세 계획 세워줘", "구현
  계획서 만들어줘", "plan 문서 작성해줘", "이 기획서로 상세 plan 만들어줘",
  "개발 계획서로 구체화해줘", or "write a detailed implementation plan".
  Reads the 기획서 and the existing codebase, interviews the user in Korean
  until every plan-shaping decision is settled, runs parallel web research
  for external facts, then writes a Korean milestone-based development plan
  (code reuse map, decision table, architecture, per-milestone deliverables
  with code sketches and verifiable completion criteria, dependency graph,
  risks, file list, checklist) and saves it following the project's
  docs/plan convention. Plans the whole 기획서 or a user-specified subset.
  Not for quick in-session coding plans and not for brainstorming a new
  idea from scratch (use idea-refiner for that).
---

# Plan Writer

Turn a converged 기획서 (idea spec) into a development plan so detailed that
coding can start the moment it is saved — real file paths, code sketches,
mechanically verifiable completion criteria — via a codebase scan, a
decision-forcing Korean interview, and a milestone-based document.

This is the step *after* `idea-refiner`: idea-refiner decides **what** to
build; plan-writer decides **exactly how**.

**Language rule:** This skill file is written in English, but **every question
you ask, every status message, and the generated plan document MUST be in
Korean (한국어).** Internal reasoning can be in any language.

## Inputs

1. **The 기획서.** Resolution order:
   - a file the user points at;
   - otherwise the most recent spec-like file (`기획서*.md`, `*spec*.md`,
     `ideas/*.md`) under the project's `docs/` or `ideas/`;
   - otherwise a spec just converged in this conversation (e.g. idea-refiner
     output on screen);
   - none of the above → ask in Korean where the spec is. Never plan from a
     one-line idea — that is idea-refiner's job; offer to run it first.
2. **The scope.** If the user names a subset ("3~6단계만", "공유 카드
   기능만"), plan exactly that subset. Default: the whole 기획서. Never
   silently widen or narrow it — e.g. when asked for "3단계만", do not also
   plan 4단계 because it "seems related".
3. **The codebase**, when the project already has code.

## How to run it

1. **Read the 기획서 fully.** Restate in 1–2 Korean sentences: the scope you
   will plan and what done looks like. Get confirmation only if scope is
   ambiguous; otherwise proceed.
   **Decomposition guard:** if the scoped work would run past ~8 milestones or
   a few weeks, say so before interviewing and propose splitting into phased
   plan docs (`<feature>-phase1-plan-v0.1.md` now, later phases later). A
   15-milestone document is one nobody follows past M3.
2. **Scan the codebase in the background — don't block.** Launch **Agent**
   subagents (`subagent_type: "Explore"`, `run_in_background: true`) to map,
   for each scoped feature: what already exists (files, functions, patterns
   to follow) vs. what must be newly built. Results become the
   `기존 코드 재활용 맵`. A brand-new project (no code yet) gets a
   `레포 디렉터리 구조` section instead of a reuse map.
3. **Interview the user — idea-refiner style.** While the scan runs, ask
   **1–3 decision-forcing Korean questions per batch**, one batch per turn,
   each targeting the *single most plan-shaping* open decision. Iterate until
   the Convergence test passes — plan-writer converges on **how** (design,
   order, criteria), not on what/why.
   - Seed the question list from: the 기획서's 미결정 사항 section, decisions
     surfaced by the codebase scan (e.g. "기존 스토어를 확장할까요, 새 모듈로
     뺄까요?"), and anything you would otherwise have to guess.
   - Prefer concrete options over open questions. 약함: "저장은 어떻게
     할까요?" 강함: "리포트 캐시는 (a) SwiftData 신규 모델 (b) 기존
     WorkoutDetailStore 확장 중 어느 쪽으로 갈까요? 트레이드오프는 …"
   - Drill vague answers immediately ("빠르게요" → "몇 초/몇 ms 기준일까요?").
   - If the user defers ("나중에 정할게"), pick a sensible default, tag it
     **🔶 가정** in the decision table, and list it under 오픈 이슈.
4. **Research external facts in parallel — never guess.** The instant an
   answer depends on an API limit, OS behavior, library capability, pricing,
   or a formula, launch background **Agent** subagents
   (`subagent_type: "general-purpose"`), one per question, all in a single
   message, each prompted: the exact question + "Use WebSearch for the latest
   sources. Return 3–5 bullet findings with source links." Fold results into
   the next interview batch and cite them in the plan's 근거 column.
5. **Write the document** in Korean following
   [references/plan-template.md](references/plan-template.md) — section
   order, table shapes, and milestone anatomy live there.
6. **Save and hand off.**
   - Folder: the project's existing plan folder (`docs/plan/`, `docs/plans/`)
     if one exists; otherwise create `docs/plan/`.
   - Filename: `<feature-slug>-plan-v0.1.md`; whole-기획서 scope →
     `<project>-plan-v0.1.md`. Bump v0.2, v0.3… on later revisions instead
     of overwriting.
   - Link the source 기획서 in the header; then report the saved path and
     suggest the next step (커밋 or "M0부터 시작할까요?").

## Tag every gap: 🔶 가정 / 🔵 오픈 질문

Same two tags `idea-refiner` uses, so a 기획서's open items carry straight into
the plan. Tag **inline where the gap appears** — in a decision row, in a
마일스톤's 핵심 작업, in a 완료 기준 — not only in 오픈 이슈:

- **🔶 가정** — a default was adopted and the plan proceeds on it. Always name
  the default. *(예: "🔶 가정: 캐시 TTL 24시간 — 사용자 보류, 기본값 채택")*
- **🔵 오픈 질문** — no answer and no safe default; must be resolved before the
  affected milestone starts. *(예: "🔵 오픈 질문: HealthKit 백그라운드 전달
  주기 — M2 착수 전 실기기 확인 필요")*

Carry the 기획서's tags forward: one you resolved in the interview becomes a
decision row with 근거; one you couldn't stays tagged and goes to 오픈 이슈.
Never let a tag vanish silently between 기획서 and plan — that is exactly the
gap that bites during implementation. And never invent a path, an API limit, or
a number to erase a tag.

## Convergence test — stop interviewing when ALL are true

- The decision table (확정 결정 모음) contains **no entry that would block
  writing code on day one** — every remaining unknown is either 🔶 with a
  stated default or 🔵 parked in 오픈 이슈 with the milestone it blocks.
- Every milestone has a goal, deliverables with **real file paths**, a
  완료 기준 a human or test can verify mechanically, and a 회귀 가드레일.
- Every reuse-map row was verified against the actual repo by the scan.
- No number, limit, or external-API fact in the plan is guessed — each is
  user-confirmed, researched (with source), or tagged 🔶.

If any fails, ask another batch or wait for research — don't pad the document
with hand-waving to finish early.

## Consistency pass — run once on the finished document, before saving

Read it as if someone else wrote it, and fix what you find inline:

- **산출물 ↔ §6 신규 파일 목록** — is §6 exactly the union of every 신설
  산출물? A row on one side only means one of them is wrong.
- **완료 기준 ↔ 기획서** — does every scoped 기획서 requirement land in some
  milestone's 완료 기준? An unlanded requirement is a hole; a 완료 기준 that
  traces back to nothing in the 기획서 is scope creep.
- **의존성 그래프 ↔ 마일스톤 순서** — does M\<k\> depend only on milestones
  before it? A backward edge means the ordering is wrong.
- **결정 테이블 ↔ 본문** — is every 확정값 actually used the way the row says?
  A decision no milestone touches was never plan-shaping — drop the row.
- **Placeholders** — any leftover "TBD", unfilled `<...>`, or 완료 기준
  readable two ways? Pick one reading and make it explicit.

Fix the mismatches. Don't list them in the document and move on.

## Hard rules

- **No invented codebase facts.** Every path in the reuse map and file list
  comes from the scan or your own reads. Violation: listing
  `Services/WeatherClient.swift` as 재활용 when no such file exists.
- **No scope beyond the 기획서 + interview answers.** Violation: adding an
  "관리자 대시보드" milestone the 기획서 never mentions because it "would be
  useful".
- **Every 완료 기준 is mechanically checkable.** Violation: "동작이
  안정화되면 완료". Instead: "시뮬레이터 목록 화면에 실내 배지 표시 +
  `StatsTests` 신규 케이스 3개 통과".
- **Plan, don't implement.** The deliverable is the document; code appears
  only as sketches inside it. Violation: creating or editing product source
  files "while we're at it".

## Output example (miniature)

Input 기획서 line:
> 3단계 | 트레드밀/야외 구분 | 목록·상세 배지, 통계 분리 집계 | 반나절

Becomes a milestone like:

````markdown
## M1 — 실내/야외 구분 데이터 계층

### 목표
모든 러닝 세션이 실내 여부 플래그를 갖고 목록/통계에서 조회 가능하다.

### 산출물
- `ios/RunWrap/WorkoutSummary.swift` — `isIndoor: Bool` 추가 (재활용·수정)
- `ios/RunWrapTests/WorkoutQueryTests.swift` — 실내 판정 케이스 (신설)

### 핵심 작업
`HKMetadataKeyIndoorWorkout` 읽기 (Bool, 부재 시 야외 취급):
```swift
let isIndoor = (workout.metadata?[HKMetadataKeyIndoorWorkout] as? Bool) ?? false
```

### 완료 기준
- 시뮬레이터: 실내 러닝 저장 → 목록에 "실내" 배지 표시
- `xcodebuild test` 신규 케이스 2개 포함 전체 통과

### 회귀 가드레일 — 깨지면 안 되는 것
- 기존 야외 러닝 카드/통계 수치가 그대로: `WorkoutQueryTests` 기존 케이스 전부 통과
````

## Style

- Same conversational Korean as idea-refiner — 짧은 배치, 강한 질문.
- Write the document for "3주 뒤의 나": explicit paths and values, never
  "적절히 처리".
- Prefer tables and text diagrams over prose walls — the template shows where.
