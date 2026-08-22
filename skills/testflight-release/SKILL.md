---
name: testflight-release
description: Ships the current dev branch to TestFlight by merging dev into main with a merge commit, so the repository's TestFlight GitHub Actions workflow fires on the main push. Runs preflight checks first — locates a TestFlight workflow under .github/workflows/ and confirms it triggers on push to main, confirms dev and main exist locally and on origin, confirms a clean worktree, and confirms local dev matches origin/dev — then shows the commits that would ship and asks for confirmation before merging, pushing, and verifying with gh run list that the workflow actually started. Use when the user asks to run a beta test or ship a TestFlight build — "베타 테스트 진행할래", "테스트플라이트 배포", "테플 올려줘", "베타 배포해줘", "dev를 main에 머지해서 배포해줘", "run a beta test", "ship a TestFlight build". Not for authoring the TestFlight workflow YAML (ios-project-setup), not for registering signing certificates or secrets (testflight-credentials), and not for App Store review submission.
---

# TestFlight Release (dev → main)

Merging `dev` into `main` is the release trigger: the repository's TestFlight
workflow runs on `push` to `main`. This skill verifies that the trigger will
actually fire, shows what ships, gets a go/no-go, then merges and confirms the
run started.

Work strictly in order — every step gates the next.

## 1. Preflight

Run this as one command from the repository root:

```bash
echo "=== workflows ===" && ls .github/workflows/ 2>/dev/null
echo "=== testflight candidates ===" && grep -ril "testflight\|upload-app" .github/workflows/ 2>/dev/null
echo "=== branches (local) ===" && git branch --list dev main
echo "=== branches (remote) ===" && git ls-remote --heads origin dev main
echo "=== worktree ===" && git status --porcelain
echo "=== current branch ===" && git rev-parse --abbrev-ref HEAD
```

Then `git fetch origin` and read the matched workflow file to confirm its
`on:` block contains `push:` with `branches: [main]`.

Finally, check sync and collect what ships:

```bash
git rev-list --left-right --count origin/dev...dev
git log --oneline --no-merges origin/main..origin/dev
```

### Gates

| Check | Pass condition | On failure |
|-------|----------------|------------|
| TestFlight workflow | A file under `.github/workflows/` matches and has a `push` trigger on `main` | **Stop.** Report which part is missing. Point to the `ios-project-setup` skill for authoring it. |
| Branches | `dev` and `main` exist both locally and on `origin` | **Stop.** Name the missing branch and ask how to proceed. |
| Worktree | `git status --porcelain` is empty | **Stop.** List the dirty files and ask the user to commit or stash first. |
| dev sync | `git rev-list --left-right --count origin/dev...dev` prints `0	0` | **Stop.** Ahead → ask to push dev first; behind → ask to pull. |
| Something to ship | `origin/main..origin/dev` is non-empty | **Stop.** Report that main is already up to date with dev. |

Never repair a failed gate on your own initiative. Violation example: the
workflow file is absent and you write a `testflight.yml` from scratch, or
`git status` is dirty and you `git stash` without asking — both are the
user's call, so stop and report instead.

## 2. Confirm

Show a Korean summary, then get explicit approval with `AskUserQuestion`
(header: `배포 진행`, options: `머지하고 배포` / `취소`).

```
사전 점검 통과
  워크플로: .github/workflows/testflight.yml (push → main 트리거 확인)
  브랜치: dev, main 로컬·원격 모두 존재 · 작업트리 clean · dev = origin/dev

배포될 커밋 3개 (main ← dev)
  89dda44 feat: 홈 상단에 앱 이름 락업 달기
  cba2ee5 feat: 요약이 끝나면 회의 제목을 내용으로 바꿔 달기 (#12)
  39192cb feat: 아이패드를 제대로 지원하기 (#10) (#13)

머지하면 main push로 TestFlight 빌드가 자동 시작됩니다.
```

Never merge or push before the user picks the approval option. Violation
example: all five gates pass, so you run `git merge` immediately because
"there is nothing left to decide" — the approval is the decision.

## 3. Merge and push

```bash
git checkout main
git pull --ff-only origin main
git merge --no-ff dev -m "chore(release): dev를 main에 머지 — TestFlight 배포"
git push origin main
git checkout dev
```

- `--no-ff` is mandatory: the release must be one merge commit even when a
  fast-forward is possible. Violation example: `git merge --squash dev` or
  `git rebase dev` — both erase the merge commit this workflow depends on.
- Always return to `dev` at the end, so the user's next command starts where
  they left off.
- On a merge conflict: run `git merge --abort`, `git checkout dev`, and report
  the conflicting files. Never resolve release conflicts yourself — the
  conflict means dev and main diverged in a way the user must review.
- Never `git push --force` to `main`, even if the push is rejected. A rejected
  push means main moved; re-run preflight instead.

## 4. Verify the run started

```bash
gh run list --workflow=testflight.yml --branch=main --limit=3
```

Use the actual matched filename. If no run for the new commit appears yet,
re-run the same command once — GitHub takes a few seconds to queue it. Do not
insert `sleep`.

Report success only when a run for the pushed commit appears in the list.
Violation example: the push succeeded, so you report "TestFlight 빌드가
시작되었습니다" without ever running `gh run list` — a disabled workflow or a
mismatched trigger silently produces no run.

## 5. Report (Korean)

```
✓ dev → main 머지 완료, TestFlight 빌드 시작
  머지 커밋: a1b2c3d (merge commit, --no-ff)
  배포 커밋: 3개
  워크플로: testflight in_progress
  실행: https://github.com/<owner>/<repo>/actions/runs/<id>
  ASC 처리까지 보통 5~15분 걸립니다.
  현재 브랜치: dev
```

When a gate stopped the run, report that instead — what failed, what the user
needs to do, and explicitly that nothing was merged or pushed.
