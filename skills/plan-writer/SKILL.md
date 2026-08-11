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
   - If the user defers ("나중에 정할게"), pick a sensible default, mark it
     `(가정)` in the decision table, and list it under 오픈 이슈.
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

## Convergence test — stop interviewing when ALL are true

- The decision table (확정 결정 모음) contains **no entry that would block
  writing code on day one** — every remaining unknown is either `(가정)` with
  a stated default or explicitly parked in 오픈 이슈.
- Every milestone has a goal, deliverables with **real file paths**, and a
  완료 기준 a human or test can verify mechanically.
- Every reuse-map row was verified against the actual repo by the scan.
- No number, limit, or external-API fact in the plan is guessed — each is
  user-confirmed, researched (with source), or marked `(가정)`.

If any fails, ask another batch or wait for research — don't pad the document
with hand-waving to finish early.

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
````

## Style

- Same conversational Korean as idea-refiner — 짧은 배치, 강한 질문.
- Write the document for "3주 뒤의 나": explicit paths and values, never
  "적절히 처리".
- Prefer tables and text diagrams over prose walls — the template shows where.
