---
name: release-tag
description: Closes out an approved App Store release of an iOS app by tagging the exact main commit that shipped it and publishing the GitHub release. Finds the commit by reading the TestFlight workflow's job logs through gh (the last upload that printed "마케팅 버전: X.Y", or the build number the user names), creates an annotated vX.Y tag there, asks before pushing, lets the repository's bump-dev-version workflow raise dev's MARKETING_VERSION to the next minor and pulls that bot commit, then drafts a Korean "주요 변경" summary from the merged PR titles and publishes it above GitHub's auto-generated notes. Use when a version has been approved for sale and needs its tag and release notes — "1.3 승인됐어 태그해줘", "릴리스 태그 달아줘", "상용 배포 마무리", "다음 버전으로 올려줘", "GitHub 릴리스 노트 써줘", "tag the release", "create the GitHub release". Not for shipping a TestFlight build (testflight-release), not for submitting to App Review (app-store-submit), and not for authoring the tag-bump workflow (ios-project-setup).
---

# Release Tag (approved version → vX.Y tag + GitHub release)

The App Store approval is the event; this skill records it in git. Three
things happen in order, and each gates the next: find the shipped commit,
tag and push it (the push lets CI bump dev to the next minor), publish the
release notes.

Everything deterministic lives in `scripts/release_tag.py`; this file only
tells you when to run it and what to decide. Run commands from the
repository root, on branch `dev` with a clean worktree.

## 1. Get the version

The user names the version ("1.3 승인됐어"). If they only say "상용 배포
마무리" without a number, read `MARKETING_VERSION` in `ios/project.yml` — the
approved version is that value (CI only bumps the patch after approval, so
`1.3` in the file means 1.3 is the train that just closed). Confirm it in one
Korean sentence before continuing.

Optional: a build number ("빌드 18이 승인됐어") pins the exact upload.

## 2. Find the commit

```bash
python3 <skill-dir>/scripts/release_tag.py find 1.3            # or: find 1.3 --build 18
```

`<skill-dir>` is this skill's directory. The script reads successful
`testflight.yml` runs on `main` and prints JSON: `pick` (the default
commit = last upload of that version, or the named build) and `candidates`
(every upload of that version, newest first). It exits non-zero with a
reason when nothing matches or the pick is not on `origin/main` — report that
reason verbatim and stop.

If `release_url` is set, the release is already done: report "이미 마무리됨"
with the tag commit and the URL, list tag / push / release as not repeated,
and stop. If only `tag_exists` is true, skip to step 4 (the tag was made
earlier; just the release is missing).

Never pick a commit by any other method. Violation example: the script finds
no 1.3 upload, so you tag the latest `main` merge because "it's probably the
one" — a wrong tag makes the bump workflow raise the wrong version and the
release notes list the wrong PRs. Stop and show the script's message instead.

## 3. Tag, confirm, push

Build the tag message from the merged PR titles since the previous tag —
`feat:` first, 4–6 phrases joined with `·`, ending in `(vX.Y)` to match the
existing tags:

```bash
git log --format='%s' vPREV..PICK_SHA | grep '^feat' | sed 's/ (#[0-9]*)//g'
git tag -a v1.3 PICK_SHA -m "release: 위젯·훈련 계획 캘린더·러닝화 마일리지·완주증 OCR (v1.3)"
```

Then show a Korean summary and get approval with `AskUserQuestion`
(header: `태그 푸시`, options: `푸시` / `취소`):

```
v1.3 태그 생성 (로컬)
  커밋: db7b739 2026-10-01 Merge pull request #205 — 1.3 빌드 18 업로드
  후보: 빌드 18 db7b739 (10-01) · 빌드 17 2d21575 (09-30) · 빌드 16 3934c1b (08-26)
  푸시하면 bump-dev-version이 dev의 MARKETING_VERSION을 1.4로 올리는 봇 커밋을 넣습니다.
```

Never push before the user picks `푸시`. Violation example: the pick is
unambiguous (one candidate), so you `git push origin v1.3` right away — the
push triggers a bot commit on `dev`, which is the user's call.

On `취소`: leave the local tag in place, say so, and stop.

On `푸시`:

```bash
git push origin v1.3
```

Then, if `.github/workflows/bump-dev-version.yml` exists, wait for its run
and pull the bot commit:

```bash
gh run list --workflow=bump-dev-version.yml --limit 1
git pull --ff-only origin dev
grep -n 'MARKETING_VERSION:' ios/project.yml
```

Re-run the `gh run list` command until the run shows `completed` (it takes
under a minute). Report success only when `project.yml` shows the next minor
(1.3 → 1.4). If the workflow file does not exist, report that dev was not
bumped and show the user the one-line edit — do not edit `project.yml`
yourself.

## 4. Release notes

Draft `summary.md` in the session scratchpad: a `## 주요 변경` heading and
at most 10 bullets, taken from the `feat:` PR titles of step 3 (drop issue
numbers, merge near-duplicates, skip `fix:`/`chore:` unless user-visible).
Every bullet must trace to a PR title in that range. Violation example:
adding "성능 개선 및 안정화" because releases usually say that — no PR title
says it, so it is invented.

Show the draft and get approval with `AskUserQuestion` (header: `릴리스
노트`, options: `이대로 게시` / `수정`). On `수정`, apply the user's edits
and ask again.

Then:

```bash
python3 <skill-dir>/scripts/release_tag.py notes 1.3 --summary summary.md > notes.md
gh release create v1.3 --title "v1.3" --notes-file notes.md
```

`notes` appends GitHub's auto-generated notes since the previous `v` tag
(PR list + Full Changelog link) below the summary — the same shape as the
repository's earlier releases. Do not pass `--generate-notes` or
`--notes-start-tag` to `gh release create`; the installed `gh` may not
support the latter, and the script already did that work.

## 5. Report (Korean)

```
✓ v1.3 릴리스 마무리
  태그: v1.3 → db7b739 (1.3 빌드 18, 2026-10-01)
  dev: MARKETING_VERSION 1.3 → 1.4 (봇 커밋 9aaf80f, pull 완료)
  릴리스: https://github.com/<owner>/<repo>/releases/tag/v1.3 (주요 변경 8줄 + PR 85건)
```

When a step stopped the run, report that instead — what failed, what the
user needs to do, and explicitly which of tag / push / release did not
happen.
