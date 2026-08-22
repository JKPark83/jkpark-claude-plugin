# CLAUDE.md Template

A Korean instruction document for the repo. Its value comes entirely from
being **true about this repo** — a generic iOS style guide is worse than no
file, because it gets trusted.

## The evidence rule

Every claim needs a source in the repo. Before writing a line, know which file
or command proves it.

| Claim | Only write it if |
|---|---|
| "의존성 없음 — SPM 미사용" | `project.yml` has no `packages:` and no `dependencies: - package:` |
| "테스트는 Swift Testing" | `grep -rl '@Test' <tests>` hits and `import XCTest` does not |
| "색은 디자인 토큰만 사용" | a token/theme source file actually exists |
| "화면 파일명은 `~Screen.swift`" | the naming holds across the existing screen files |
| "주석은 한국어" | existing comments are in fact Korean |
| "포매터 없음 — 주변 스타일에 맞춘다" | no `.swiftformat` / `.swiftlint.yml` |

Writing "색상 리터럴 금지, 디자인 토큰만 사용" into a repo with no theme file
is the failure this rule exists to prevent: the next session obeys a rule
nobody made, and starts inventing a token system.

When a section has no verified content, **omit the section**. An empty
"아키텍처" heading is better than a guessed three-layer diagram, and no
heading at all is better than an empty one.

## Sections, in order

Fixed skeleton — the first four are always written (they follow from
xcodegen + the repo scan), the rest appear only when the scan found material.

### 1. 헤더 (always)

One line naming the app, its platform floor, and what it does; then links to
`README.md` and any spec under `docs/` that exists.

```markdown
# {{APP}} — Claude 작업 지침

{한 줄 설명} (iOS {deployment target}+, SwiftUI).
개요는 [README](README.md), 제품 결정은 [기획서](docs/plan/기획서-v0.1.md) 참조.
```

Drop a link whose target does not exist rather than linking a file to create
later.

### 2. 프로젝트·스택 (always)

A table straight from the detection results. Rows with no verified value are
dropped, not filled with "미정".

```markdown
| 항목 | 값 |
|---|---|
| 스킴 / 프로젝트 | `{{APP}}` / `{{IOS_DIR}}/{{APP}}.xcodeproj` (워크스페이스 없음) |
| 타깃 | `{{APP}}`(앱), `{{APP}}Tests`(유닛 테스트) |
| 배포 타깃 | iOS {version} |
| 기본 시뮬레이터 | {{SIM}} |
| 의존성 | {packages 나열 또는 "**없음** — SPM·CocoaPods 모두 미사용"} |
| 테스트 | {framework} {N}개 (`{{IOS_DIR}}/{{APP}}Tests`) |
| 포매터·린터 | {설치된 것 또는 "없음. 주변 코드 스타일을 눈으로 맞춘다"} |
```

### 3. 절대 하지 말 것 (always)

The generated-file prohibitions must match the guard hook's branches exactly —
if the hook blocks `NepNepWidgets/Info.plist`, this section names it too. A
document that permits what the hook denies wastes a turn on every occurrence.

```markdown
- `*.xcodeproj/` 내부, 특히 `project.pbxproj`를 편집하지 않는다.
  **생성물이고 gitignore 대상**이다. 타깃 멤버십이 어긋나면
  `{{IOS_DIR}}/project.yml`을 고쳐 xcodegen을 다시 돌린다.
  같은 이유로 {생성되는 Info.plist·entitlements 경로 나열}도 직접 편집 금지.
- `xcodebuild`를 직접 쓰지 않는다. 아래 MCP 도구를 쓴다.
- 비밀값을 커밋하지 않는다. ({DEVELOPMENT_TEAM}은 비밀이 아닌 팀 ID다.)
```

Add repo-specific prohibitions only for things the scan found: a data file a
workflow overwrites on a schedule, a privacy boundary the code actually
enforces (e.g. HealthKit data that never leaves the device). Do not add a
privacy rule to an app that has no such data.

### 4. 빌드·검증 (always)

```markdown
`*.xcodeproj`와 생성되는 plist·entitlements는 전부 생성물이다 —
**`{{IOS_DIR}}/project.yml`만 수정**하고 xcodegen으로 재생성한다.

```bash
cd {{IOS_DIR}} && xcodegen generate    # 이것만 셸에서 직접 실행한다
```

이후 빌드·테스트·실행은 XcodeBuildMCP 도구로 한다
(`projectPath: {{IOS_DIR}}/{{APP}}.xcodeproj`, `scheme: {{APP}}`,
`simulatorName: {{SIM}}`):

| 용도 | 도구 |
|---|---|
| 빌드 | `XcodeBuildMCP:build_sim` |
| 테스트 | `XcodeBuildMCP:test_sim` |
| 빌드+설치+실행 | `XcodeBuildMCP:build_run_sim` |
| 스크린샷 | `XcodeBuildMCP:screenshot` |
| 시뮬레이터 목록 | `XcodeBuildMCP:list_sims` |
```

Then the CI facts, written only when the corresponding workflow was actually
produced: TestFlight uploads on `main` merge, the build number comes from ASC
+1 so `CURRENT_PROJECT_VERSION` needs no hand-editing, and `MARKETING_VERSION`
is a minimum wish CI may bump.

### 5. 완료 기준 (always)

```markdown
1. 빌드가 깨끗하다. 새 경고가 생기면 무시하지 말고 보고한다.
2. UI를 바꿨으면 `build_run_sim`으로 시뮬레이터에 띄우고 `screenshot`으로
   의도와 대조한다. 2~5회 고쳐도 어긋나면 무엇이 다른지 설명하고 멈춘다.
3. 관련 테스트를 돌려 통과시킨다. 실패하는 테스트를 지우거나 비활성화하지 않는다.
4. 검증한 것만 보고한다. 돌려보지 않은 코드를 동작한다고 말하지 않는다.
```

Record the warning baseline in item 1 when a build was actually run during
setup; otherwise leave the baseline out rather than asserting "경고 0건".

### 6. 아키텍처 (only if layers are visible)

Write it when file naming or directory structure shows a real separation
(engines / stores / screens, `Core/` vs `Features/`). One table row per layer:
files, and the rule that layer follows. Skip for a flat repo.

### 7. 코딩 스타일 (only what the code shows)

Sub-sections for 일반 / SwiftUI / 테스트, each carrying rules read out of the
existing code: comment language, observation pattern in use (`ObservableObject`
vs `@Observable` — name the one actually used and say the other is not mixed
in), localization or hardcoded Korean strings, naming conventions, test naming.

### 8. 커밋 (always)

Derive the convention from `git log --oneline -30`. If the history uses
`feat:` / `fix:` prefixes with Korean summaries, write that; if it does not,
write what it does use. Do not impose Conventional Commits on a repo that has
never used them.

Always end with: `- **시키기 전에는 커밋·푸시하지 않는다.**`

### 9. 확실하지 않을 때 (always)

```markdown
- 모르는 API는 추측하지 말고 확인한다. 배포 타깃(iOS {version})과 빌드 SDK가
  다르므로, 최신 SDK에서 컴파일된다고 배포 타깃에서 도는 것은 아니다 —
  가용성 확인 필수.
- 기존에 있는 것부터 찾는다. 같은 일을 하는 헬퍼를 새로 만들기 전에 한 번 검색한다.
```

## Merging into an existing CLAUDE.md

Keep every existing line. Append only sections whose **content** the file
lacks — match on what a section covers, not on its heading text. An existing
`## 스택 / 식별자` table already covers `프로젝트·스택`; appending a second
table under the template's heading duplicates it. Likewise `## 컨벤션`
usually covers 코딩 스타일 and 커밋: fold the one mandated missing line
(`시키기 전에는 커밋·푸시하지 않는다.`) into it rather than opening a rival
`## 커밋` section.

Show the user the list of sections to add before writing.

If the existing file contradicts a section you would add — e.g. it tells the
reader to run `xcodebuild` directly while the template routes builds through
XcodeBuildMCP — do not silently overwrite and do not append both and let the
reader sort it out. Surface it as one of Step 2's decisions and write whatever
the user picked.

## Length

Aim for 80–150 lines, and count the **merged total**, not just what you
appended. When merging would blow past that, drop template sections whose
substance the file already has rather than trimming the user's own text. Cut
the generic advice first; the repo-specific prohibitions earn their space.
