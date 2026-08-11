# Plan Document Template

Derived from the user's real plan docs (binance-coach
`strategy-board-backtest-plan.md`, trade-coach `IMPLEMENTATION_PLAN.md`).
Everything below the guidance notes is the Korean skeleton to fill in.
Sections marked *(조건부)* appear only when their condition holds — drop them
silently otherwise. Keep every table's column set exactly as shown.

## Header

```markdown
# <기능/프로젝트> 개발 계획서 (v0.1)

작성일: <YYYY-MM-DD> | 버전: v0.1 | 베이스 커밋: <branch @ short-hash>

**한 줄 요약:** <이 계획이 무엇을, 어떤 접근으로 만드는지 한 문장.>

관련 문서: [<기획서 이름>](<상대 경로>)
```

- 베이스 커밋 = `git log -1 --format="%h"` on the current branch at write
  time; new project without git → `(신규 저장소)`.
- 계획 범위가 기획서의 일부라면 한 줄 요약에 범위를 명시
  ("로드맵 3~6단계만 다룬다").

## 목차

Include a linked 목차 when the document has 8+ top-level sections; omit for
short plans.

## 0. 전제 — 기존 코드 재활용 맵 *(기존 프로젝트)*

The single most load-bearing section: it pins the plan to reality. Every row
comes from the codebase scan — real paths only.

```markdown
## 0. 전제 — 기존 코드 재활용 맵

| 구분 | 재활용 (그대로/확장) | 신설 (새로 만든다) |
|---|---|---|
| <영역: 데이터, UI, 저장, …> | `<실제/경로/파일>` — <어떻게 쓰는지> | `<새 파일 경로>` — <역할> |
```

**신규 프로젝트일 때 이 섹션을 통째로 교체:**

````markdown
## 0. 레포 디렉터리 구조

```
<project>/
├── <dir>/
│   ├── <file>      # <역할 주석>
```
````

Full tree of every planned file, one comment per non-obvious entry
(trade-coach style).

## 1. 확정 결정 모음

Every decision from the interview + research, one row each, so later sections
never re-argue them. `(가정)` marks defaults the user deferred.

```markdown
## 1. 확정 결정 모음

| 항목 | 확정값 | 근거 |
|---|---|---|
| <결정할 것> | <단일 확정값> | <사용자 답변 / 리서치 출처 링크 / 기획서 §n> |
| <미룬 결정> | <기본값> (가정) | 사용자 보류 — 오픈 이슈 #n |
```

## 2. 아키텍처

Text diagram of runtime/data flow (box-and-arrow ASCII, like the 기획서's §5
and trade-coach's §1) + a stack table **only for parts this plan touches**:

```markdown
| 영역 | 선택 | 비고 |
|---|---|---|
```

Small scoped plans (single milestone, no new moving parts) may omit the
diagram and keep only the table.

## 3. 마일스톤 M0 ~ Mn

The core. Rules:

- **M0 is always 준비** — dependencies, migrations, scaffolding, config —
  ending with "기존 앱/테스트가 여전히 정상"인 상태.
- One milestone = 반나절~수일 of work, independently verifiable, ordered by
  dependency. Half-day items may be merged; anything over ~1주 must be split.
- Anatomy per milestone (all four parts, always):

```markdown
## M<k> — <이름>

### 목표
<한 문장: 이 마일스톤이 끝나면 무엇이 참이 되는가.>

### 산출물
- `<파일 경로>` — <신설 | 재활용·수정> <무엇이 들어가는지>

### 핵심 작업
<순서 있는 작업. 까다로운 지점엔 코드 스케치 — DDL, 함수 시그니처,
핵심 알고리즘/수식, 헷갈리기 쉬운 API 호출. 스케치는 "무엇을 어떻게"가
드러나는 최소 분량 — 완성 코드를 미리 쓰는 자리가 아니다.>

### 완료 기준
- <기계적으로 확인 가능한 항목: 명령 + 기대 결과, 화면 + 기대 표시>
- <테스트: 어떤 테스트가 새로 생기고 통과해야 하는가>
```

## 4. 의존성 그래프 · 병렬화 지점

```markdown
M0 ─→ M1 ─→ M2 ─┬→ M3 (M2와 병렬 가능)
                └→ M4
```

One line per 병렬화 기회 explaining why it's safe. Linear plans: single
chain + "병렬화 지점 없음".

## 5. 위험 요소와 완화책

```markdown
| 위험 | 확률 | 영향 | 완화책 |
|---|---|---|---|
```

Plan-level risks only (구현 순서·기술 선택이 무산될 수 있는 지점). Product
risks stay in the 기획서 — don't copy them here.

## 6. 신규 파일 목록 (전체)

Flat list of every file the milestones create, grouped by directory — the
"did I forget something" cross-check. Must equal the union of all 산출물
entries marked 신설.

## 7. 완료 체크리스트

```markdown
- [ ] M0: <완료 기준 요약 한 줄>
- [ ] M1: …
- [ ] 전체: <최종 E2E 확인 한 줄 — 예: "실기기에서 흐름 X 완주">
```

Always keep the 전체 row as its own last line, even when it restates the
final milestone's criterion — it is the one box that means "쓸 수 있는 상태".

## 8. 오픈 이슈 *(있을 때만)*

Every `(가정)` the plan proceeds on — decisions the user deferred in the
interview AND assumptions the writer had to make (unresolvable by 기획서,
interview, or research). One entry each: what is open, the default adopted,
and what would change in the plan if decided otherwise. Empty → omit the
section entirely.
