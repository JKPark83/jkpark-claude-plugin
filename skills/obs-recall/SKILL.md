---
name: obs-recall
description: Search the user's Obsidian vault as a personal knowledge base. Use when the user asks whether something was previously saved, researched, or summarized (e.g. "예전에 정리한 거 있나?", "볼트에서 찾아봐", "obs에서 검색해줘"), or when past research notes in the vault could inform the current task.
model: sonnet
---

# Obsidian 지식저장소 검색 (obs-recall)

## 목적

사용자의 Obsidian vault를 지식저장소로 활용해, 과거에 저장해 둔 분석·조사·정리 노트를 찾아 현재 질문/작업에 반영한다.

## Vault 설정

- **Vault 경로**: 환경변수 `OBSIDIAN_VAULT`가 있으면 그 값을 쓰고, 없으면
  `~/workspace/obsidian/MyObsidian`을 기본값으로 쓴다. 아래 셸 스니펫에서는
  `$VAULT`로 참조한다.

  ```bash
  VAULT="${OBSIDIAN_VAULT:-$HOME/workspace/obsidian/MyObsidian}"
  ```

- **인덱스**: `Home.md` — 모든 노트가 폴더별 섹션에 `- [[노트 제목]] — 요약` 형식으로 등록되어 있다.
- **폴더 구조** (주제 기준):

| 폴더 | 들어있는 것 |
|------|------------|
| `Inbox/` | 분류 전 빠른 캡처 (`{제목}.md` 단일 파일) |
| `Projects/` | 특정 프로젝트의 코드·구조·이슈 분석 |
| `Documents/` | 가이드·온보딩·설계 문서 |
| `Paper/` | 논문 해설·정리 |
| `Research/` | 프로젝트 무관 기술 조사·딥리서치 |
| `Archive/` | 보관용 (현행 아닐 수 있음 — 인용 시 시점을 밝힌다) |

- **folder-note 패턴**: `Inbox/`를 제외한 모든 노트는 `{폴더}/{제목}/{제목}.md`에 있고, HTML·이미지 첨부가 같은 폴더에 함께 있다. 본문의 핵심 내용이 `.md`가 아니라 **첨부 HTML에만 있는 경우가 많다** (`.md`는 요약과 링크만 담기도 한다).

## 검색 절차 (인덱스 → 태그 → 본문 순)

### 1. 인덱스 확인 (가장 저렴한 경로)

`Home.md`를 읽고 제목·요약에서 관련 노트 후보를 고른다. 여기서 충분히 찾았으면 3단계는 생략한다.

### 2. frontmatter 태그 검색

```bash
grep -rl "^tags:.*{키워드}" "$VAULT" --include="*.md"
```

### 3. 본문 키워드 검색

인덱스와 태그로 못 찾았을 때만 수행한다. 한국어/영어 동의어 변형을 2~3개 시도한다 (예: "스케줄" / "schedule" / "cron").

`.md`에는 요약만 있고 실제 내용은 첨부 HTML에 있는 경우가 많으므로 **`.md`와 `.html`을 함께 검색한다**:

```bash
grep -rli "{키워드}" "$VAULT" \
  --include="*.md" --include="*.html" --exclude-dir=".obsidian"
```

### 4. 노트 읽기 및 반영

- 후보 노트의 `.md`를 먼저 Read로 읽는다. 요약만 있고 세부가 필요하면 같은 폴더의 HTML을 읽는다.
- HTML은 CSS·스크립트 때문에 그대로 읽으면 노이즈가 크다. 본문 텍스트만 추출해서 본다:

```bash
python3 -c "
import re,sys,html
s=open(sys.argv[1],encoding='utf-8').read()
s=re.sub(r'(?is)<(script|style|head).*?</\1>',' ',s)
s=re.sub(r'(?s)<[^>]+>',' ',s)
print(html.unescape(re.sub(r'[ \t]+',' ',s)).strip())
" "{HTML 경로}"
```

- 답변에 반영할 때 **출처 노트의 볼트 내 경로를 명시**한다 (예: `Research/LiteLLM 상세 조사/LiteLLM 상세 조사.md`).
- 노트의 `created` 시점을 확인하고, 오래된 기술 정보는 현행과 다를 수 있음을 감안한다. 코드·설정 관련이면 현재 코드베이스와 대조 후 사용한다.
- `Archive/`의 노트는 사용자가 더 이상 활발히 참조하지 않는 자료다. 인용할 때 보관본임을 밝힌다.

### 5. 검색 결과가 없을 때

"볼트에 관련 노트가 없다"고 명확히 보고한다. 추측으로 있는 척하지 않는다.

## 주의사항

- `.obsidian/` 디렉터리는 검색 대상에서 제외한다.
- 볼트는 사용자의 개인 저장소다 — 검색·읽기만 하고, 이 스킬에서 노트를 수정·삭제하지 않는다. 저장이 필요하면 `/obs` 스킬을 사용한다.
