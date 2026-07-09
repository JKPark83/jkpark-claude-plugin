---
name: obs
description: Save content to Obsidian vault as a folder-note with frontmatter tags, then update the Home.md index. Use when the user wants to record Claude's response, a note, analysis artifacts, or any content to their Obsidian vault. Auto-routes by topic into Projects/Documents/Paper/Research/Inbox and bundles attachments alongside the note.
model: sonnet
---

# Obsidian에 노트 저장 (obs)

## 목적

현재 대화 내용이나 사용자가 원하는 내용을 Obsidian vault에 frontmatter(태그 포함)가 붙은 마크다운 노트로 저장하고, 볼트 인덱스(`Home.md`)를 갱신한다.

## Vault 설정

- **Vault 경로**: 환경변수 `OBSIDIAN_VAULT`가 있으면 그 값을 쓰고, 없으면
  `~/workspace/obsidian/MyObsidian`을 기본값으로 쓴다. 아래 셸 스니펫에서는
  `$VAULT`로 참조한다.

  ```bash
  VAULT="${OBSIDIAN_VAULT:-$HOME/workspace/obsidian/MyObsidian}"
  ```

  **Vault 이름**은 경로의 마지막 디렉터리명이다 (`basename "$VAULT"`). 완료 보고의
  `obsidian://` 링크에 쓴다.

- **폴더 구조** (주제 기준 분류):

| 폴더 | 용도 | frontmatter type |
|------|------|------------------|
| `Inbox/` | 분류 전 빠른 캡처 (주제가 애매할 때) | `note` |
| `Projects/{제목}/` | 특정 프로젝트의 코드·구조·이슈 분석 아티팩트 | `analysis` |
| `Documents/{제목}/` | 가이드·온보딩·설계 문서 | `document` |
| `Paper/{제목}/` | 논문 해설·정리 | `paper-summary` |
| `Research/{제목}/` | 프로젝트에 종속되지 않는 기술 조사·딥리서치 | `research` |
| `Archive/{제목}/` | 더 이상 활발히 참조하지 않는 보관용 노트. **자동 라우팅 대상이 아니며**, 사용자가 `/obs Archive/`로 명시하거나 기존 노트를 여기로 이동할 때만 사용 | (원본 type 유지) |

### 폴더-노트(folder-note) 패턴

`Inbox/`를 제외한 **모든 폴더는 folder-note 패턴을 따른다**. 첨부파일 유무와 무관하다.

```
{폴더}/{제목}/{제목}.md      ← 노트 (폴더명 = 노트명)
{폴더}/{제목}/*.html, *.png  ← 첨부파일 (있으면 같은 폴더에)
```

- 노트 파일명에 타임스탬프를 넣지 않는다. 작성 시각은 frontmatter `created`로만 기록한다.
- 첨부파일만 폴더에 두고 `.md`를 빠뜨리면 Obsidian에서 노트로 열리지 않는다. **`.md`는 항상 함께 생성한다.**
- `Inbox/`만 예외로 폴더 없이 `{제목}.md` 단일 파일로 저장한다.

## 실행 단계

### 1. 인자 파싱

`/obs` 호출 시 인자를 다음 규칙으로 파싱한다:

| 인자 형식 | 설명 | 예시 |
|-----------|------|------|
| 인자 없음 | 직전 Claude 응답 전체를 저장 (폴더는 자동 라우팅) | `/obs` |
| `폴더명/` (끝에 `/`) | 지정 폴더에 저장, 내용은 직전 응답 | `/obs Research/` |
| `"제목"` (따옴표) | 제목 지정, 내용은 직전 응답 | `/obs "LangGraph 정리"` |
| `폴더명/ "제목"` | 폴더 + 제목 지정 | `/obs Paper/ "ReAct 논문 정리"` |
| 내용을 직접 입력 | 해당 텍스트를 노트로 저장 | `/obs 오늘 배운 것: ...` |

### 2. 저장 폴더 자동 라우팅

사용자가 폴더를 명시하지 않았으면 **내용의 주제**로 판단한다 (첨부파일 유무는 판단 기준이 아니다):

- 논문 해설·정리 → `Paper/{제목}/`
- 특정 프로젝트의 코드·구조·이슈 분석 결과 → `Projects/{제목}/`
- 프로젝트에 종속되지 않는 기술 조사·딥리서치 → `Research/{제목}/`
- 사용법 가이드·온보딩 문서·설계 문서 → `Documents/{제목}/`
- 판단이 애매하면 → `Inbox/`

판단 순서는 위에서 아래로 적용한다. 예를 들어 "특정 프로젝트에 논문 기법을 적용한 분석"은 `Paper/`가 아니라 `Projects/`다 — 주된 대상이 프로젝트 코드이기 때문이다.

> `Archive/`는 자동 라우팅 후보에서 제외한다. 사용자가 `/obs Archive/`로 명시할 때만 저장한다.

### 3. 태그 결정 (기존 태그 재사용 우선)

태그 난립을 막기 위해 **볼트에 이미 존재하는 태그를 우선 재사용**한다:

```bash
# 볼트 내 기존 frontmatter 태그 수집
VAULT="${OBSIDIAN_VAULT:-$HOME/workspace/obsidian/MyObsidian}"
grep -rhoE '^tags: \[[^]]*\]' "$VAULT" --include="*.md" | sort -u
```

- 수집된 기존 태그 중 내용과 맞는 것을 우선 선택한다.
- 새 태그가 필요하면 **영어 소문자 kebab-case**로 만든다 (예: `langgraph`, `code-review`, `sse`). 한국어 고유 도메인 용어는 한국어 허용.
- 태그는 2~5개로 제한한다.

### 4. Frontmatter 작성

노트 상단에 다음 형식으로 붙인다:

```yaml
---
created: {YYYY-MM-DD HH:MM}
source: claude-code
project: {관련 프로젝트명}   # 특정 프로젝트 관련일 때만. 아니면 키 자체를 생략
type: analysis | document | paper-summary | research | note
tags: [태그1, 태그2]
---
```

`type`은 저장 폴더와 1:1로 대응한다 (`Projects/`→`analysis`, `Documents/`→`document`, `Paper/`→`paper-summary`, `Research/`→`research`, `Inbox/`→`note`).

### 5. 관련 노트 위키링크

`Home.md` 인덱스를 읽어 주제가 관련된 기존 노트가 있으면, 노트 본문 맨 아래에 섹션을 추가한다:

```markdown
## 관련 노트

- [[ReAct 논문 정리]]
```

위키링크는 `.md` 확장자를 뺀 **파일명 전체**를 사용한다. 관련 노트가 없으면 이 섹션은 생략한다.

### 6. 첨부파일 동반 저장

저장 대상에 파일(HTML 리포트, 이미지, 스크립트, PDF 등)이 함께 있으면, **라우팅된 폴더를 바꾸지 않고** 같은 folder-note 폴더 안에 넣는다:

1. 첨부파일들을 `{폴더}/{제목}/` 안에 복사한다 (노트 `.md`와 같은 폴더).
2. 노트 본문에서 `![[파일명.png]]` (이미지) 또는 `[[파일명.html]]` (기타) 형식으로 임베드·링크한다.
3. HTML이 여러 장이면 진입점(`index.html`)을 먼저 링크하고, 나머지는 목록으로 각 장의 한 줄 설명과 함께 링크한다.

> 첨부가 있다고 해서 `Documents/`로 보내지 않는다. 논문 해설 HTML은 `Paper/`, 딥리서치 HTML은 `Research/`에 둔다.

### 7. 파일 저장

```
vault_root = $OBSIDIAN_VAULT (없으면 ~/workspace/obsidian/MyObsidian)
title      = 사용자 지정 제목 | 내용을 요약한 제목(최대 50자) | "Note"
created    = 현재 시각 (KST, `date "+%Y-%m-%d %H:%M"` 으로 확인) → frontmatter에만 기록

경로 = "{vault_root}/{폴더}/{title}/{title}.md"   # Inbox는 "{vault_root}/Inbox/{title}.md"
```

- 폴더가 없으면 `mkdir -p`로 생성한다.
- Write 툴로 파일을 생성한다.
- 같은 이름의 폴더/파일이 이미 있으면 덮어쓰지 않고 제목에 `(1)`, `(2)`를 붙인다.
- 파일명으로 쓸 수 없는 문자(`:`, `*`, `?`, `"`, `<`, `>`, `|`, `\`, `/`)는 `_`로 치환한다.
- **`.md` 없이 첨부파일만 저장하고 끝내지 않는다.** 저장 후 `{제목}/{제목}.md`가 실제로 존재하는지 확인한다.

### 8. Home.md 인덱스 갱신

`Home.md`의 해당 폴더 섹션(`## Projects`, `## Paper`, `## Research`, `## Documents`, `## Inbox`, `## Archive`)에 한 줄을 추가한다:

```markdown
- [[{노트 제목}]] — {한 줄 요약}
```

위키링크는 `.md`를 뺀 노트 파일명(= 폴더명 = 제목)을 쓴다. 섹션은 폴더와 1:1이며, 새 섹션을 임의로 만들지 않는다.

### 9. 완료 보고

```
✓ Obsidian에 저장했습니다.
  경로: {folder}/{filename}
  태그: {태그 목록}
  열기: obsidian://open?vault={vault 이름}&file={URL인코딩된 경로}
```

## 예시

```
/obs
→ (직전 응답이 agent-builder 스케줄 서비스 분석이면)
  Projects/스케줄 서비스 분석/스케줄 서비스 분석.md

/obs Research/ "LiteLLM 상세 조사"
→ Research/LiteLLM 상세 조사/LiteLLM 상세 조사.md

/obs (ReAct 논문 해설 HTML 여러 장과 함께)
→ Paper/ReAct 논문 정리/ReAct 논문 정리.md
  Paper/ReAct 논문 정리/index.html, 01-background.html, ...

/obs Inbox/ "나중에 정리할 메모"
→ Inbox/나중에 정리할 메모.md      (Inbox만 폴더 없이 단일 파일)
```
