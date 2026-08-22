# Hook Templates

Two hooks. Substitute `{{APP}}`, `{{IOS_DIR}}` and the detected generated-file
paths; write the Korean comments and deny messages so they name *this* repo.
`chmod +x` both after writing.

Both scripts **fail open** — every unexpected condition is `exit 0`. A hook
that dies loudly blocks every edit in the session; a hook that misses one case
costs a regenerated file.

---

## `.claude/hooks/block-generated-files.sh`

PreToolUse on `Edit|Write|NotebookEdit`. Denies edits to files xcodegen owns.

Why it matters: an edit to a generated file appears to work — the build even
picks it up — and then vanishes at the next `xcodegen generate`. That is the
hardest failure mode to notice, so it is blocked outright.

### Branch construction

One `case` branch per generated artifact found in `project.yml`.

**The pattern is built from the declared path, never from the target name.**
`info.path` is a path relative to `IOS_DIR` and is frequently *not* named
after the target — `targets.TeslaSync.info.path: App/Info.plist` must produce
`*/App/Info.plist|App/Info.plist`, not `*/TeslaSync/Info.plist`. A pattern
built from the target name silently matches nothing, and a guard hook that
matches nothing is worse than no hook: it reports success while protecting
nothing.

| Detected | Pattern to match | Deny message points at |
|---|---|---|
| always | `*/project.pbxproj\|*.xcodeproj/*\|*.xcodeproj` | the `project.yml` that generates it |
| `targets.T.info.path: <P>` | `*/<P>\|<P>` | `targets.T.info.properties` |
| `targets.T.entitlements.path: <P>` | `*/<P>\|<P>` | `targets.T.entitlements.properties` |

The `\|<P>` alternation catches a repo-root-relative path with no leading
segment; without it, an `info.path` at the top of `IOS_DIR` can slip through.

Only `info.path:` / `entitlements.path:` keys make a file generated. A plist
referenced through `INFOPLIST_FILE` or `CODE_SIGN_ENTITLEMENTS` build settings
is a **hand-authored source file** — blocking it stops legitimate edits, so
leave it out.

Multiple `project.yml` files (e.g. an app plus a spike project) → say "같은
디렉터리의 project.yml" in the `.xcodeproj` branch and name the app's path in
parentheses. Omit a branch entirely when the corresponding key is absent —
do not emit an entitlements branch for a repo that has no entitlements.

### Template

```bash
#!/usr/bin/env bash
# 생성물 파일 편집 차단 (PreToolUse / Edit·Write·NotebookEdit)
#
# 왜: 이 프로젝트에서 .xcodeproj·Info.plist는 전부 xcodegen이
# {{IOS_DIR}}/project.yml에서 만들어 내는 생성물이고 .gitignore 대상이다.
# 직접 고치면 다음 `xcodegen generate`에서 조용히 날아가고, 그 사이 빌드가 나는
# 바람에 고쳐진 것처럼 보인다 — 가장 알아채기 어려운 실패라 아예 막는다.
#
# 대상: {{감지된 생성물 목록}}
#
# 실패 방식: 경로를 못 읽거나(jq 실패·payload 이상) 패턴에 안 걸리면 exit 0으로
# 조용히 통과시킨다. 차단은 오탐이 나도 사람이 바로 알아채지만, 훅이 죽어서
# 모든 편집이 막히는 쪽은 훨씬 나쁘다.
set -uo pipefail

payload=$(cat)
path=$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_input.notebook_path // empty' 2>/dev/null)
[ -z "$path" ] && exit 0

deny() {
  jq -n --arg r "$1" '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: $r
    }
  }'
  exit 0
}

case "$path" in
  */project.pbxproj|*.xcodeproj/*|*.xcodeproj)
    deny "생성물이라 편집할 수 없습니다: ${path}
*.xcodeproj는 xcodegen이 {{IOS_DIR}}/project.yml에서 생성합니다.
{{IOS_DIR}}/project.yml을 고치고 \`cd {{IOS_DIR}} && xcodegen generate\`를 실행하세요."
    ;;
  # 아래는 targets.{{TARGET}}.info.path 값 그대로 — 타깃 이름이 아니다
  */{{INFO_PATH}}|{{INFO_PATH}})
    deny "생성물이라 편집할 수 없습니다: ${path}
Info.plist는 {{IOS_DIR}}/project.yml의 targets.{{TARGET}}.info.properties에서 생성됩니다.
거기를 고치고 \`cd {{IOS_DIR}} && xcodegen generate\`를 실행하세요."
    ;;
  */{{ENTITLEMENTS_PATH}}|{{ENTITLEMENTS_PATH}})
    deny "생성물이라 편집할 수 없습니다: ${path}
entitlements는 {{IOS_DIR}}/project.yml의 targets.{{TARGET}}.entitlements.properties에서 생성됩니다.
거기를 고치고 \`cd {{IOS_DIR}} && xcodegen generate\`를 실행하세요."
    ;;
esac

exit 0
```

### Worked instantiations

**Target name == folder name.** `project.yml` at `ios/`, `name: NepNep`,
targets `NepNep` (`info.path: NepNep/Info.plist`) and `NepNepWidgets`
(`info.path: NepNepWidgets/Info.plist`), no entitlements → three branches:
the `.xcodeproj` one, `*/NepNep/Info.plist|NepNep/Info.plist`, and
`*/NepNepWidgets/Info.plist|NepNepWidgets/Info.plist`. The entitlements
branch is dropped.

**Target name != folder name — the case that breaks a name-based pattern.**
`project.yml` at the repo root, `name: TeslaSync`, target `TeslaSync` with
`info.path: App/Info.plist`; a second target `TeslaSyncBroadcast` whose plist
and entitlements come from `INFOPLIST_FILE` / `CODE_SIGN_ENTITLEMENTS` build
settings. → two branches only: the `.xcodeproj` one and
`*/App/Info.plist|App/Info.plist`. Nothing for `TeslaSyncBroadcast` — its
files are hand-authored sources. A branch reading `*/TeslaSync/Info.plist`
would be the defect this section exists to prevent.

---

## `.claude/hooks/swift-format.sh`

PostToolUse on `Edit|Write`. Formats the just-edited `.swift` file.

Ships **intentionally inert**: it does nothing until the repo has both the
`swiftformat` binary and a `.swiftformat` config. Running SwiftFormat with
default options on an existing codebase rewrites every file into someone
else's style — the opposite of "don't change existing style". The header
comment must say so, and the final report must state whether it is active.

```bash
#!/usr/bin/env bash
# Swift 파일 자동 포맷 (PostToolUse / Edit·Write)
#
# 왜: 편집 직후에 포맷을 맞춰 두면 리뷰 diff에 스타일 잡음이 섞이지 않는다.
#
# 지금은 조건이 안 맞아 아무 일도 하지 않는다 — 의도된 상태다.
# 이 저장소에는 SwiftFormat도, .swiftformat 설정 파일도 없다. 설정 없이
# 기본값으로 돌리면 기존 코드를 전부 남의 스타일로 갈아엎어
# "기존 스타일을 바꾸지 않는다"는 원칙을 정면으로 어긴다.
#
# 켜는 법 (둘 다 있어야 동작한다):
#   1. brew install swiftformat
#   2. 저장소 루트에 .swiftformat 작성 — 기존 코드에서 규칙을 뽑아내려면
#      `swiftformat --inferoptions {{IOS_DIR}}/{{APP}} > .swiftformat`
#   3. 처음 한 번은 전체에 적용하고 별도 커밋으로 분리한다 (diff 잡음 격리)
#
# 실패 방식: 어느 조건이든 안 맞으면 exit 0으로 조용히 통과한다.
# 포매터가 실패해도 편집 자체를 되돌리지는 않는다.
set -uo pipefail

payload=$(cat)
file=$(printf '%s' "$payload" | jq -r '.tool_response.filePath // .tool_input.file_path // empty' 2>/dev/null)
[ -z "$file" ] && exit 0

case "$file" in
  *.swift) ;;
  *) exit 0 ;;
esac

command -v swiftformat >/dev/null 2>&1 || exit 0

root=$(git -C "$(dirname "$file")" rev-parse --show-toplevel 2>/dev/null) || exit 0
[ -f "$root/.swiftformat" ] || exit 0

swiftformat --config "$root/.swiftformat" "$file" >/dev/null 2>&1 || true
exit 0
```

When the repo **already has** `.swiftformat` and `swiftformat` installed,
rewrite the "지금은 조건이 안 맞아…" paragraph to state that the hook is
active and which config it uses. Do not ship the "inert" comment on a repo
where the hook actually runs.
