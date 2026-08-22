---
name: app-store-metadata
description: Drafts the text an iOS app needs for App Store review — name, subtitle, promotional text, description, keywords, what's new, support/marketing URLs, copyright, App Review notes, the App Privacy label, age-rating answers, and a screenshot shot list — by scanning the repository (PRD/docs, project.yml, Info.plist usage descriptions, network call sites, privacy/terms URLs) so every claim traces to evidence, not invention. Writes a Korean draft (English locale optional) under docs/release/ for review, then fills App Store Connect fields with claude-in-chrome only after the user approves — never clicking 심사에 추가, 제출, or any submit control. Use when preparing an App Store submission or store metadata — "앱 심사 제출 준비해줘", "앱스토어 설명 써줘", "심사 메모 작성해줘", "개인정보 영양표 채워줘", "키워드 뽑아줘", "prepare App Store metadata", "write the app description". Not for TestFlight signing (testflight-credentials), shipping a build (testflight-release), CI workflows (ios-project-setup), or release notes alone from git history (app-store-changelog).
---

# App Store Review Metadata

Every field on the App Store Connect version page is a claim Apple will check
against the binary. This skill derives those claims from the repository, writes
them to a reviewable draft, and only then types them into App Store Connect.

Work strictly in order — each step feeds the next.

**The one rule that governs all of it:** every sentence in the output traces to
a file in the repo, a live URL, or an answer the user gave in Step 2. Nothing
else. Violation example: writing "AI가 회의 중 실시간으로 요약해 드립니다" when
the pipeline only runs after the recording stops — plausible marketing copy,
but the reviewer opens the app and finds no live summary, and it becomes a
2.3.1 rejection.

## 1. Scan the repository

Run as one command from the repo root:

```bash
echo "=== docs ===" && ls docs/ docs/plan/ 2>/dev/null
echo "=== project spec ===" && ls **/project.yml *.xcodeproj Info.plist 2>/dev/null
echo "=== usage descriptions ===" && grep -rn "UsageDescription\|CFBundleDisplayName\|MARKETING_VERSION\|TARGETED_DEVICE_FAMILY\|UIBackgroundModes\|ITSAppUsesNonExemptEncryption" --include=project.yml --include=Info.plist . 2>/dev/null
echo "=== features ===" && ls */Features */Core 2>/dev/null
echo "=== network egress ===" && grep -rln "URLSession\|https://" --include=*.swift . 2>/dev/null | head -20
echo "=== tracking/analytics ===" && grep -rln "AppTrackingTransparency\|Firebase\|Amplitude\|Mixpanel\|Sentry\|AdSupport" --include=*.swift --include=*.yml . 2>/dev/null
echo "=== IAP ===" && grep -rln "StoreKit\|Product.purchase\|subscription" --include=*.swift . 2>/dev/null | head
```

Then read, in this order: the PRD or README (positioning, differentiators,
target user), any release checklist under `docs/`, `project.yml` (display name,
version, device family, permissions, background modes), and the feature
directory names (they map to the description's feature list).

Record what each file gives you. That record becomes the 근거 column in Step 3
— if a field has no source, it goes to Step 2 instead of being invented.

### Gates

| Check | Pass condition | On failure |
|-------|----------------|------------|
| App identity | Display name, bundle ID, and marketing version found | **Stop.** Ask the user for the missing value; do not guess a name from the directory. |
| Positioning source | A PRD, README, or spec describes what the app does and for whom | Ask the user to describe it in Step 2 — do not write positioning from source-file names alone. |
| Privacy/terms URLs | Two reachable URLs exist | Ask in Step 2. Apple requires a privacy policy URL; the field cannot be left empty. |
| Egress inventory | Every host in the network scan is accounted for | **Stop.** An unexplained endpoint means the privacy label cannot be answered honestly. |

## 2. Interview — only the gaps

One `AskUserQuestion` call (batch up to 4), covering only what the scan could
not answer. Typical gaps:

- **Locales** — Korean only, or Korean + English (header: `작성 언어`).
- **Version type** — first submission (설명 전체 작성) vs. update (새로운 소식
  중심, 설명은 기존 유지) (header: `제출 유형`).
- **Demo access** — does the reviewer need an account, sample data, or a
  specific device capability? Ask what the reviewer must do to see the main
  feature within two minutes.
- **Anything a gate flagged** — support URL, copyright holder, privacy URL.

Never ask what the repo already answered. Violation example: asking "이 앱의
주요 기능이 뭔가요?" when `docs/PRD.md` opens with a one-line definition — read
it and confirm in one sentence instead.

## 3. Write the draft

Save to `docs/release/app-store-metadata.md` (create the directory if needed;
follow the repo's existing docs convention when it has one).

Field constraints, ASC field names, and screenshot sizes:
[references/asc-fields.md](references/asc-fields.md).
Privacy nutrition label and age rating derivation:
[references/privacy-and-rating.md](references/privacy-and-rating.md).

Use this template verbatim — section order and headings included:

```markdown
# {앱 이름} v{버전} App Store 심사 메타데이터

| 항목 | 값 |
|---|---|
| 번들 ID | com.example.App |
| 버전 | 1.0 |
| 로케일 | 한국어 (ko) |
| 근거 스캔 시점 | {커밋 해시} |

## 1. 스토어 텍스트

### 앱 이름 (30자)
{값}  ← {n}자

### 부제 (30자)
{값}  ← {n}자

### 프로모션 텍스트 (170자)
{값}  ← {n}자

### 키워드 (100자)
{쉼표로 구분, 공백 없음}  ← {n}자

### 설명 (4,000자)
{본문}  ← {n}자

### 새로운 소식 (4,000자)
{값 — 첫 제출이면 "첫 출시" 한 줄}

### URL·저작권
| 필드 | 값 |
|---|---|
| 지원 URL | {url} |
| 마케팅 URL | {url 또는 비움} |
| 저작권 | {연도} {보유자} |

## 2. 앱 심사 정보

### 로그인 필요 여부
{필요 없음 / 필요 — 계정 정보}

### 연락처
{이름 · 이메일 · 전화 — 사용자 확인 필요}

### 심사 메모 (4,000자)
{값}  ← {n}자

## 3. 개인정보 영양표

| 데이터 유형 | 수집 | 근거 |
|---|---|---|
| … | 안 함 | {파일:줄} |

## 4. 연령 등급

| 설문 항목 | 답변 | 근거 |
|---|---|---|

## 5. 스크린샷 계획

| # | 화면 | 캡션 | 근거 화면 |
|---|---|---|---|

## 6. 사람이 채워야 하는 항목

- [ ] {항목} — {이유}
```

Writing rules:

- **Character counts are computed, not estimated.** Print the actual count
  next to every limited field, and cut before you hand it over. Violation
  example: a 182-character promotional text delivered with "170자 이내로
  맞췄습니다" — App Store Connect silently truncates on paste and the store
  page ships a half sentence.
- **Keywords carry no spaces after commas** and never repeat the app name or
  subtitle (both are already indexed). `회의록,녹음,전사,화자분리,노션` — not
  `회의록, 녹음, 회의록 앱`.
- **The description leads with the differentiator, not the category.** Open
  with what the app does that others do not, then the feature list, then
  limitations. Violation example: "회의록을 만들어주는 앱입니다" as the first
  line — true of every competitor, and it wastes the two lines shown before
  "더 보기".
- **No superlatives, competitor names, pricing, platform references, or
  "beta"** anywhere in store text. `국내 최고의`, `클로바노트보다 정확한`,
  `안드로이드에서도 사용 가능`, `무료 체험 후 월 4,900원` all trigger review
  rejection or metadata rework.
- **The review note answers "how do I see the main feature in two minutes".**
  Include: whether login is needed, what to tap in order, what sample data to
  use, and any capability the simulator lacks. Violation example: a note that
  only says "온디바이스로 동작합니다" — the reviewer still does not know that
  they must grant the microphone permission and record for 30 seconds before
  anything appears.
- **Unresolved items go to section 6, never to a plausible guess.** A contact
  phone number the repo does not contain is a checklist item, not a
  placeholder that looks real.
- **Section 6 holds only what blocks a field in this document** — a missing
  value, an ASC questionnaire the user must answer, or an asset to upload.
  Cap it at eight items. Violation example: the repo's release checklist also
  lists secret rotation, third-party console setup, signing certificates, and
  regression tests, so you copy them into section 6 — none of them fills a
  metadata field, and they bury the three values you actually need from the
  user. Mention such items in one line outside the document if they block
  submission at all.

## 4. Review with the user

Show sections 1–2 inline in the conversation (they are what ships to users),
summarize 3–5 in one line each, and read section 6 aloud as a list. Then ask
with `AskUserQuestion` (header: `다음 단계`):

| Option | Effect |
|--------|--------|
| `App Store Connect에 입력` | Proceed to Step 5. |
| `초안만 두기` | Stop here; report the file path. |
| `수정하고 다시` | Take the edit, rewrite the file, re-ask. |

Stop at the draft unless the user picks the first option. Violation example:
the draft looks complete, so you open App Store Connect and start typing
because "the user asked for submission prep" — entering the fields is a
separate decision.

## 5. Enter into App Store Connect

Load the browser tools in one call, then navigate:

```
ToolSearch: select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__read_page,mcp__claude-in-chrome__form_input,mcp__claude-in-chrome__get_page_text
```

Ask the user for the App Store Connect app ID if the repo does not record it,
then open `https://appstoreconnect.apple.com/apps/{appId}/distribution/ios/version/inflight`.
If the page shows a sign-in form, stop and ask the user to log in themselves —
never type Apple ID credentials.

Fill in this order, and after every field group press the page's 저장 button
and re-read the page to confirm the value stuck:

1. 프로모션 텍스트 → 설명 → 키워드 → 지원 URL → 마케팅 URL → 저작권
2. 앱 심사 정보: 로그인 필요 여부 → 연락처 → 메모
3. 새로운 소식 (updates only)

Leave these to the user and say so explicitly: screenshot uploads, the App
Privacy questionnaire, the age-rating questionnaire, build selection, pricing,
and release-timing choice. They are multi-step wizards where a wrong answer
persists across versions.

**Never click 심사에 추가, 제출, 심사를 위해 제출, or any button that advances
the version state.** Violation example: all fields are filled and the page
shows 심사에 추가 as enabled, so you click it to "finish the task" — submitting
to review is irreversible for that build and is the user's decision alone.

If a field rejects the value (length, invalid URL), report which field and
why; do not silently shorten the text that the user already approved.

## 6. Report (Korean)

```
✓ App Store 심사 메타데이터 초안 작성
  파일: docs/release/app-store-metadata.md
  근거: docs/PRD.md · ios/project.yml · docs/plan/출시-준비-체크리스트.md
  텍스트: 이름 3자 · 부제 24자 · 프로모션 118자 · 키워드 96자 · 설명 1,842자
  개인정보 영양표: 수집 안 함 (근거 4건) · 연령 등급: 4+
  App Store Connect 입력: 텍스트 6필드 + 심사 정보 3필드 저장 확인

  사람이 해야 하는 항목 3건
  - 스크린샷 6.9"·13" 업로드 (계획은 초안 5절)
  - 개인정보 설문 직접 제출 (답안은 초안 3절)
  - 심사 연락처 전화번호

  제출 버튼은 누르지 않았습니다.
```

When a gate stopped the run, report that instead — what was missing, what the
user needs to supply, and that nothing was entered into App Store Connect.
