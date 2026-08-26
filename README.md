# jkpark-claude-plugin

개인용 [Claude Code](https://docs.claude.com/en/docs/claude-code) 플러그인.
스킬 14개 + 에이전트 1개 + 훅 1개 + 상태줄(옵션)로 구성된다.

## Skills

### 기획 · 계획

| 스킬 | 하는 일 | 트리거 예시 |
|------|---------|-------------|
| `idea-refiner` | 막연한 아이디어를 한국어 Q&A로 파고들어 바로 만들 수 있는 스펙으로 수렴 | "이런 기능 어떨까?" |
| `plan-writer` | 기획서 + 코드베이스 스캔 + 인터뷰 → 코드 수준 한국어 마일스톤 구현 계획서 | "이 기획서로 상세 plan 만들어줘" |

### 글쓰기 · 문서

| 스킬 | 하는 일 | 트리거 예시 |
|------|---------|-------------|
| `tech-blog-writer` | 주제/링크를 주니어 눈높이의 이미지 풍부한 한국어 기술 블로그 HTML로 작성·발행 | "이 주제로 기술 블로그 써줘" |
| `obs-html` | 인터뷰 → 이미지 포함 독립형 한국어 HTML 문서 → obs로 볼트 저장 | "HTML로 정리해서 볼트에 넣어줘" |
| `obs-ppt` | 인터뷰 기반 16:9 PPT형 HTML 슬라이드 덱(키보드 내비·발표자 노트) → obs 저장 | "이거 슬라이드로 만들어줘" |

### Obsidian 지식베이스

| 스킬 | 하는 일 | 트리거 예시 |
|------|---------|-------------|
| `obs` | 내용을 태그 달린 folder-note로 볼트에 저장하고 `Home.md` 인덱스 갱신 | "이거 볼트에 저장해줘" |
| `obs-recall` | 볼트를 인덱스 → 태그 → 전문 순으로 검색 (첨부 HTML 포함, 읽기 전용) | "예전에 정리한 거 있나?" |

> 볼트 경로는 `$OBSIDIAN_VAULT`, 기본값 `~/workspace/obsidian/MyObsidian`.

### iOS 개발 · 배포

| 스킬 | 하는 일 | 트리거 예시 |
|------|---------|-------------|
| `ios-project-setup` | xcodegen 리포 스캔 → 훅·CLAUDE.md·settings·TestFlight CI 워크플로 셋팅 | "iOS 프로젝트 초기 셋팅 해줘" |
| `testflight-credentials` | App ID·배포 인증서(.p12)를 API로 생성하고 GitHub 시크릿 5종 등록 | "TestFlight 올릴 준비 해줘" |
| `testflight-release` | 프리플라이트 → dev→main 머지 커밋 푸시 → TestFlight 워크플로 기동 확인 | "테플 올려줘" |
| `app-store-metadata` | 리포 근거 기반 심사 메타데이터(설명·키워드·개인정보 라벨 등) 초안 → 승인 후 ASC 입력 | "앱 심사 제출 준비해줘" |

### 투자

| 스킬 | 하는 일 | 트리거 예시 |
|------|---------|-------------|
| `us-monthly-dividend` | 미국 월배당 포트폴리오 설계·분석 — 1~12월 배당 달력, 세후(15% 원천징수) 현금흐름, 배당컷 OK/WARN/REVIEW 판정 (yfinance 스크립트 기반), obs 저장 | "월배당 포트폴리오 짜줘" |

### 유틸리티 · 메타

| 스킬 | 하는 일 | 트리거 예시 |
|------|---------|-------------|
| `analyze-image` | 이미지 분석 요청 시 macOS 클립보드를 먼저 확인해 바로 읽음 (macOS 전용) | "방금 캡쳐한 거 봐바" |
| `skill-generator` | 인터뷰 → SKILL.md 생성/개선 → 체크리스트·매칭·행동 평가 3중 검증 → 플러그인 등록 | "스킬 만들어줘" |

## Agents / Hooks / Status line

| 구성요소 | 내용 |
|----------|------|
| `korean-reviewer` (agent) | 생성된 한국어 문서(.md/.html/.pptx)의 번역투·어색한 표현을 교정하는 Sonnet 서브에이전트 |
| PostToolUse hook | 문서 파일이 쓰이면 korean-reviewer 실행을 자동 제안 (advisory, 차단 없음) |
| Status line (옵션) | 작업 중 🤖🧠 / 대기 😴💤 애니메이션 상태줄 — `statusline/`을 직접 복사해 설치 ([가이드](statusline/README.md)) |

## 설치

```bash
# 로컬 (이 리포에서)
/plugin marketplace add ./
/plugin install jkpark-claude-plugin@jkpark-plugins

# GitHub에서
/plugin marketplace add JKPark83/jkpark-claude-plugin
/plugin install jkpark-claude-plugin@jkpark-plugins
```
