---
name: ios-project-setup
description: >-
  Use when the user wants an iOS app repository wired up for Claude Code and
  CI — openers like "iOS 프로젝트 초기 셋팅 해줘", ".claude 룰셋 만들어줘",
  "훅이랑 CLAUDE.md 세팅해줘", "TestFlight 자동 배포 워크플로 추가해줘",
  "이 앱도 runwrap처럼 셋팅해줘", "set up .claude for this iOS app", or
  "add a TestFlight workflow". Scans the repo for its real values (scheme,
  targets, bundle ID, team ID, deployment target, generated Info.plist and
  entitlements paths, test framework, dependencies) and then writes six
  artifacts: a PreToolUse hook blocking edits to xcodegen-generated files, a
  PostToolUse SwiftFormat hook, a merged .claude/settings.json, a Korean
  CLAUDE.md written only from what the scan verified, and GitHub Actions
  workflows for TestFlight upload on main merge and dev version bumping on
  release tags. Requires an xcodegen project.yml and stops if absent. Merges
  into existing files, never overwrites them, and never commits. Not for
  writing app code, fixing build errors, or drafting App Store release notes.
---

# iOS Project Setup

Lay down the Claude Code ruleset and GitHub Actions CI for an **xcodegen-based**
iOS app repo, with every project-specific value read out of the repo rather
than guessed.

**Language rule:** this skill file is English, but **every question, status
line, and generated artifact — CLAUDE.md prose, hook deny messages, workflow
comments, commit-message conventions — MUST be in Korean (한국어).**

## What it produces

| Artifact | Purpose |
|---|---|
| `.claude/hooks/block-generated-files.sh` | PreToolUse guard — denies edits to `*.xcodeproj`, generated `Info.plist`, generated `*.entitlements` |
| `.claude/hooks/swift-format.sh` | PostToolUse formatter — inert until both `swiftformat` and `.swiftformat` exist |
| `.claude/settings.json` | registers both hooks (merged into any existing file) |
| `CLAUDE.md` | Korean project instructions, filled from the scan |
| `.github/workflows/testflight.yml` | main merge → test → archive → TestFlight upload |
| `.github/workflows/bump-dev-version.yml` | release tag push → bump `MARKETING_VERSION` on `dev` |

Plus, only with the user's agreement in Step 2, two version keys added to
`project.yml` — the workflows cannot run without them. That is the entire
blast radius; nothing else in the repo is modified.

Full file templates live in `references/hooks.md`, `references/workflows.md`,
and `references/claude-md.md`. Read a reference only when you reach the step
that writes its artifact.

If the user asked for a subset ("워크플로만", "훅만 깔아줘"), produce exactly
that subset and skip the other steps — do not add CLAUDE.md because it "goes
together".

## Preconditions

Verify in one Bash call before anything else:

```bash
git rev-parse --show-toplevel && find . -name project.yml -not -path '*/.*' | head
```

- **Not a git repo** → stop. The workflows and the hooks' repo-root lookup both
  need one.
- **No `project.yml` with a `targets:` key** → stop with a Korean explanation:
  this skill assumes xcodegen, every artifact it writes is built on that
  assumption, and introducing xcodegen to an existing `.xcodeproj` is a
  separate job. Ask whether to do that first; do not proceed by improvising a
  non-xcodegen variant.
- **`.xcodeproj` tracked by git** (`git ls-files --error-unmatch <name>.xcodeproj` succeeds)
  → report it and continue. The guard hook still helps, but note in the final
  report that the `.xcodeproj` should be gitignored and removed from the index.

## Step 1 — Detect

Read `project.yml` (plus `git`, the tests directory, and `.swiftformat`) and
fill this table. Never invent a value; leave it `미확인` and resolve it in
Step 2.

| Value | Source | Fallback |
|---|---|---|
| `APP` / scheme | `project.yml` top-level `name:` | 미확인 |
| `IOS_DIR` | directory containing `project.yml` (e.g. `ios`); repo root when it sits at the top | — |
| Targets + types | `targets:` keys and their `type:` | 미확인 |
| `BUNDLE_ID` | app target's `PRODUCT_BUNDLE_IDENTIFIER`, else `options.bundleIdPrefix` + `.` + app target name | 미확인 |
| `TEAM_ID` | `settings.base.DEVELOPMENT_TEAM` | 미확인 |
| Deployment target | `options.deploymentTarget.iOS` | 미확인 |
| Generated plist/entitlements paths | every target's `info.path:` and `entitlements.path:`, **verbatim** | none — omit those hook branches |
| `MARKETING_VERSION` | `settings.base.MARKETING_VERSION`, as a quoted string | 없음 — see below |
| `CURRENT_PROJECT_VERSION` | `settings.base.CURRENT_PROJECT_VERSION`, as a quoted string | 없음 — see below |
| Test target | `targets:` entry of type `bundle.unit-test` | none — drop the test step from CI |
| Test framework | `grep -rl '@Test' <tests dir>` → Swift Testing, else XCTest | 해당없음 when there is no test target — never `미확인` |
| Dependencies | `packages:` block | 없음 |
| `DEV_BRANCH` | `dev` only if `git rev-parse --verify dev` succeeds | 없음 — see below |
| Formatter | `.swiftformat` present? `command -v swiftformat`? | 없음 |
| `SIM` | `XcodeBuildMCP:list_sims` → newest runtime, then the plain `Pro` model of the newest generation (not `Max`, not `e`, not `Air`) | `iPhone 17 Pro` |

Three rows decide whether an artifact gets written at all — resolve them
before Step 5, never paper over them:

- **`MARKETING_VERSION` / `CURRENT_PROJECT_VERSION` absent.** Both workflows
  regex these keys out of `project.yml` and crash on the first run without
  them (`AttributeError` in `testflight.yml`, an explicit `SystemExit` in
  `bump-dev-version.yml`). Absent → offer to add them to
  `settings.base` (`MARKETING_VERSION: "1.0"`, `CURRENT_PROJECT_VERSION: "1"`)
  in Step 2. Writing the workflows against a `project.yml` that lacks them is
  a violation — they are guaranteed-broken CI.
- **No `dev` branch.** Then `DEV_BRANCH` is 없음 and `bump-dev-version.yml` is
  **skipped**, not retargeted. Falling back to the default branch produces a
  workflow that bot-commits to `main` on every release tag — a materially
  different action from "advance the long-lived dev branch", and one nobody
  asked for.
- **`TEAM_ID` present but not a paid team.** The ID itself carries no tier, so
  grep the prose for it: `grep -rin '무료\|free team\|개인 팀\|personal team' <project.yml> README.md docs/`.
  The marker often sits in `README.md` or `docs/`, not next to the key — a
  check that only reads `project.yml` comments misses it. TestFlight requires
  a paid Apple Developer Program membership, so a syntactically valid
  free-team ID still cannot upload. Presence alone does not clear this row.
  Finding no marker anywhere means "no evidence either way" — proceed, and say
  in the report that the tier was not verified.

Also record every existing artifact the run would touch (`.claude/settings.json`,
either hook, either workflow, `CLAUDE.md`) — Step 3 onward branches on this.

## Step 2 — Confirm

Print the detected table in Korean and ask with **one** `AskUserQuestion` call.

Ask about every `미확인` value, **plus these decisions even when nothing is
`미확인`** — a resolved table does not mean there is nothing to decide:

| Condition | Question | Default if the user does not decide |
|---|---|---|
| `MARKETING_VERSION` / `CURRENT_PROJECT_VERSION` 없음 | add them to `project.yml`, or skip the workflows? | **add them** — a two-line edit beats losing CI |
| `DEV_BRANCH` 없음 | skip `bump-dev-version.yml`, or create a `dev` branch first? | **skip the workflow** |
| `TEAM_ID` looks like a free team | write `testflight.yml` anyway, or hold until a paid team is set? | **hold** — a free team cannot upload |
| Existing `CLAUDE.md` contradicts a section to be added | keep the existing line, or replace it? | **keep the existing line**, and drop only the contradicting part of the new section — not the whole section |

Adding the two version keys is the one write outside the six artifacts.
Nothing else in `project.yml` may be touched: reordering its keys or
"fixing" an unrelated build setting while in there is a violation.

Never ask for a value the scan already resolved — asking "번들 ID가 뭔가요?"
when `project.yml` has `bundleIdPrefix: com.nepnep` and a target named
`NepNep` is a violation of this step.

If the table is fully resolved *and* none of the four conditions holds, print
the table and proceed without a question.

## Step 3 — Hooks

Read `references/hooks.md` and write both scripts, substituting the detected
values. Then `chmod +x` both.

The guard hook's deny branches come from the detection table, not from the
template's examples. A generated hook that still contains `*/NepNep/Info.plist`
in a repo whose app target is `RunWrap` is a violation — every path and every
Korean deny message names *this* repo's targets and its `project.yml` path.

Both hooks must **fail open**: any unreadable payload, missing `jq`, or missing
tool exits 0. A hook that blocks every edit because `jq` is absent is worse
than a hook that misses a case.

## Step 4 — settings.json

**Merge, never replace.** Read the existing `.claude/settings.json` (if any),
append the two hook entries into the matching event arrays, and leave every
other key untouched.

Input — existing file:

```json
{
  "hooks": {
    "PostToolUse": [
      { "matcher": "Bash", "hooks": [{ "type": "command", "command": "./scripts/log.sh" }] }
    ]
  }
}
```

Output:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|NotebookEdit",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PROJECT_DIR:-.}/.claude/hooks/block-generated-files.sh\"",
            "timeout": 10,
            "statusMessage": "생성물 편집 여부 확인 중"
          }
        ]
      }
    ],
    "PostToolUse": [
      { "matcher": "Bash", "hooks": [{ "type": "command", "command": "./scripts/log.sh" }] },
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PROJECT_DIR:-.}/.claude/hooks/swift-format.sh\"",
            "timeout": 30,
            "statusMessage": "Swift 포맷 적용 중"
          }
        ]
      }
    ]
  }
}
```

The pre-existing `Bash` entry survives. If an entry pointing at the same script
path is already present, leave it alone and report it as 이미 있음.

## Step 5 — Workflows

Read `references/workflows.md` and write the two files, substituting the
detected values.

**An existing workflow file is never overwritten.** Diff it against the
template and report the differences instead, so the user decides. Replacing a
hand-tuned `testflight.yml` because it "drifted from the template" is a
violation — the repo's version is the source of truth once it exists.

Skip an artifact, and say so in the report, whenever Step 2 left it unusable:
`testflight.yml` when there is no usable `TEAM_ID`, `bump-dev-version.yml`
when `DEV_BRANCH` is 없음, and both when the version keys are missing and the
user declined to add them. A skipped workflow named in the report is a
result; a workflow that fails on its first run is a defect.

## Step 6 — CLAUDE.md

Read `references/claude-md.md`, then write the document in Korean.

**Every line must be traceable to something the scan verified.** Writing
"색은 디자인 토큰만 사용한다" into a repo that has no theme file is a
violation — that rule belongs in the document only when a `Theme.swift`-style
token source actually exists. Sections with nothing verified are omitted, not
filled with plausible-sounding defaults.

When `CLAUDE.md` already exists, **merge**: keep the existing text as-is and
append only the sections it lacks, under their own headings. Never rewrite the
user's existing prose to match the template's wording.

## Step 7 — Secrets

Report status only. Run:

```bash
gh secret list 2>/dev/null | cut -f1
```

Compare against the five `testflight.yml` needs — `ASC_KEY_ID`,
`ASC_ISSUER_ID`, `ASC_KEY_P8`, `DIST_CERT_P12_BASE64`, `DIST_CERT_PASSWORD` —
and list the missing ones with the one-line "where to get it" notes from
`references/workflows.md`.

**Never run `gh secret set`, and never ask the user to paste a secret value
into the conversation.** Offering "`.p8` 내용을 붙여넣어 주시면 등록해 드릴게요"
is a violation — the value would land in the transcript and the shell history.
If `gh` is missing or unauthenticated, say the check was skipped.

## Step 8 — Verify

Prove the artifacts work before reporting. Do not skip a check because the file
"obviously" works.

```bash
# 1. .xcodeproj 를 차단하는가 (경로는 감지 결과로 바꿔 쓴다)
echo '{"tool_input":{"file_path":"'"$PWD/$IOS_DIR/$APP"'.xcodeproj/project.pbxproj"}}' \
  | .claude/hooks/block-generated-files.sh
# → permissionDecision: "deny" 가 나와야 한다

# 2. 감지된 생성물 경로를 하나씩 실제로 차단하는가 — 반드시 info.path 값 그대로 넣는다
echo '{"tool_input":{"file_path":"'"$PWD/$IOS_DIR"'/App/Info.plist"}}' \
  | .claude/hooks/block-generated-files.sh
# → deny. 통과해 버리면 패턴이 실제 경로와 어긋난 것이다 (가장 흔한 결함)

# 3. 훅이 무관한 파일은 통과시키는가
echo '{"tool_input":{"file_path":"'"$PWD"'/README.md"}}' | .claude/hooks/block-generated-files.sh
# → 출력 없음 + 종료코드 0

# 4. settings.json 이 유효한 JSON 인가
jq empty .claude/settings.json

# 5. 워크플로가 유효한 YAML 인가
python3 -c "import yaml,sys;[yaml.safe_load(open(f)) for f in sys.argv[1:]]" .github/workflows/*.yml

# 6. project.yml 이 여전히 생성되는가
cd "$IOS_DIR" && xcodegen generate
```

Any failure → fix and re-run that check. Report only checks that actually ran:
if `xcodegen` is not installed, say `xcodegen 미설치로 6번 생략` rather than
claiming the project generates.

## Step 9 — Report

Korean, in this shape:

```
✓ iOS 프로젝트 셋팅 완료 — {repo}

감지된 값
  스킴 {APP} · 번들 {BUNDLE_ID} · 팀 {TEAM_ID} · iOS {deployment target} · 시뮬 {SIM}
  타깃 {targets} · 테스트 {framework, N개} · 의존성 {packages}

생성
  .claude/hooks/block-generated-files.sh   차단 대상 {N}종
  .claude/hooks/swift-format.sh            {비활성 — .swiftformat 없음 | 활성}
  .claude/settings.json                    {신규 | 기존에 훅 2건 추가}
  CLAUDE.md                                {N}줄
  .github/workflows/testflight.yml
  .github/workflows/bump-dev-version.yml

건너뜀
  {기존 파일 · 차이점 요약}

검증
  훅 차단 ✓ / 통과 ✓ · settings.json ✓ · 워크플로 YAML ✓ · xcodegen ✓

남은 일
  리포 시크릿 {missing}개 등록 필요 — {이름 나열}
  {필요 시} ios/{APP}.xcodeproj 를 .gitignore 에 넣고 인덱스에서 제거

커밋은 직접 진행해주세요 (/commit 사용 가능)
```

**Never commit or push.** Creating the files and then running `git commit`
because "셋팅이 끝났으니" is a violation — the user commits.
