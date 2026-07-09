---
name: obs-html
description: >-
  Use when the user wants a topic written up as a self-contained, image-rich
  Korean HTML document and filed into their Obsidian vault. Triggers on "이 주제로
  HTML 문서 만들어서 obs에 저장해줘", "HTML로 정리해서 볼트에 넣어줘", "obs-html",
  "/obs-html", or any request to produce an HTML write-up destined for Obsidian.
  Always interviews the user first (AskUserQuestion) to pin down length and the
  concrete requirements, writes natural Korean at a junior-friendly level, embeds
  at least one visual per major section, then hands the finished HTML to the obs
  skill for folder-note filing and Home.md indexing.
---

# obs-html — HTML 문서를 써서 Obsidian에 정리·저장

주제 하나를 받아서 **자체 완결형(self-contained) HTML 문서**로 쓰고, 그것을
**`obs` 스킬을 통해 Obsidian 볼트에 folder-note로 저장**한다.

이 스킬 파일은 영어로 쓰여 있지만, **사용자에게 보이는 모든 것 — 문서 본문,
제목, 캡션, 질문, 완료 보고 — 은 반드시 한국어**로 쓴다. 코드·식별자·정착된 영어
기술 용어(commit, cache, deploy …)는 그대로 둔다.

## 절대 규칙

1. **인터뷰 없이 쓰기 시작하지 않는다.** 반드시 `AskUserQuestion`으로 분량과
   구체적 요구사항을 먼저 확정한다 (아래 1단계).
2. **그림 없이 저장하지 않는다.** 주요 섹션마다 최소 1개의 시각 자료(다이어그램·
   이미지·차트)를 넣는다 (5단계).
3. **번역투 금지.** 한국 사람이 읽었을 때 어색한 문장이 하나도 없어야 한다.
4. **저장은 `obs` 스킬에 위임한다.** 볼트 경로·폴더 라우팅·`Home.md` 갱신 규칙을
   여기서 다시 구현하지 않는다.

---

## 워크플로

```
1. 인터뷰 (AskUserQuestion)  →  2. 리서치  →  3. 개요 확인
   →  4. 집필 (한국어)  →  5. 시각 자료 삽입  →  6. HTML 렌더
   →  7. obs 스킬로 저장  →  8. 완료 보고
```

### 1. 인터뷰 — 필수, 건너뛰지 않는다

`AskUserQuestion`을 **한 번의 호출로** 최대 4개 질문을 묶어 던진다. 최소 아래 두
가지는 반드시 포함한다.

**질문 A — 총 분량** (header: `분량`)

| 옵션 | 설명 |
|------|------|
| 요약 (1~2쪽) | 핵심만. A4 1~2장, 대략 1,500~2,500자 |
| 표준 (3~5쪽) | 배경 + 본론 + 예시. 4,000~7,000자 (권장) |
| 상세 (6~10쪽) | 심화 설명·다중 예제·비교표. 10,000자 이상 |

**질문 B — 문서 성격** (header: `문서 성격`)

기술 문서인지 아닌지에 따라 눈높이가 달라지므로 반드시 확정한다.

- `기술 문서` — 코드·아키텍처·API. **주니어 개발자가 읽고 따라올 수 있는 수준.**
- `비기술 문서` — 기획·리서치·개념 설명. **전공자가 아니어도 이해할 수 있게 쉽게 풀어서.**

**질문 C·D — 주제별 구체 요구사항 (매번 새로 만든다)**

주제를 보고 정말로 갈리는 지점을 골라 묻는다. 예시 (그대로 베끼지 말 것):

- 독자 (팀 내부 온보딩용 / 외부 공개용 / 나만 볼 정리)
- 다뤄야 할 범위 (개념까지만 / 실전 예제 포함 / 대안 비교까지)
- 코드 예제 언어, 강조할 관점, 반드시 포함할 항목

옵션은 서로 배타적으로 쓰고, 권장안이 있으면 첫 번째에 두고 라벨 끝에
`(권장)`을 붙인다. 애매하면 사용자가 "Other"로 자유 입력할 수 있다.

인터뷰 답변을 **한두 문장의 한국어로 되짚어 확인**한 뒤 다음 단계로 넘어간다.

### 2. 리서치 — 추측하지 않는다

지어내면 안 되는 항목(현재 버전, API 제약, 벤치마크 수치, 흔한 실수, 대안)을
3~6개 뽑는다. `Agent` 툴(`subagent_type: "general-purpose"`)로 **질문 하나당
에이전트 하나씩, 한 메시지에 모두, `run_in_background: true`** 로 병렬 조사한다.
각 에이전트에게: 정확한 질문 + *"WebSearch로 최신 출처를 찾고, 각 항목마다 출처
링크가 붙은 4~6개 불릿으로 답하라."*

- 놀랍거나 문서의 핵심을 떠받치는 주장은 **독립된 출처 2개 이상**으로 교차 확인.
- 모든 출처 URL을 보관한다 → 마지막 `참고 자료` 섹션이 된다.

이미 잘 아는 주제이고 사용자가 빠른 정리를 원하면 리서치는 생략해도 되지만,
**최신 버전·수치를 문서에 쓸 거라면 반드시 확인한다.**

### 3. 개요 확인 — 짧게

한국어 목차(섹션 + 한 줄 설명)를 제시하고 확인받는다. 여기서 붙잡고 늘어지지
않는다. 기본 골격 (자유롭게 변형):

```
도입 — 왜 필요한가, 어떤 문제를 푸는가
배경 — 따라오는 데 필요한 최소한의 사전 지식
본론 — 섹션별 설명 + 그림 + (기술 문서면) 코드
실전 예제 / 적용
흔한 실수 · 팁
마무리 — 한눈에 보는 요약
참고 자료 — 출처 링크
```

### 4. 집필 — 자연스러운 한국어

`references/writing-style.md`를 **읽고** 나서 쓴다. 핵심:

- **기술 문서**: 독자는 주니어 개발자. 기본 문법은 설명하지 말되, 중급 이상의
  개념·전문 용어·"왜 중요한지"는 반드시 풀어준다. 비유를 적극 사용한다.
- **비기술 문서**: 배경지식 없는 사람도 읽히게. 전문 용어는 처음 등장할 때 괄호로
  풀어 쓰고, 추상적인 설명은 구체적인 예시로 받쳐준다.
- **번역투를 쓰지 않는다.** 영어 자료를 옮길 때는 단어가 아니라 **의미**를 옮긴다.
- 문장은 짧게. 한 문단은 3~5문장. 능동태 우선.
- 리서치에서 가져온 내용은 `참고 자료`의 링크로 추적 가능해야 한다.

작성 후 `korean-reviewer` 에이전트가 자동으로 붙는다(플러그인 훅). 지적된 어색한
표현은 **저장 전에 반영**한다.

### 5. 시각 자료 — 반드시 넣는다

**주요 섹션마다 최소 1개.** 우선순위 순으로 고른다:

1. **인라인 SVG 다이어그램** — 구조·흐름·관계를 직접 그린다. 외부 의존이 없어
   HTML 하나로 완결되고, Obsidian에서도 그대로 보인다. **기본 선택지.**
2. **인라인 SVG 차트** — 수치 비교. 차트를 그리기 전에 `dataviz` 스킬을 읽는다.
3. **웹 이미지** — 공식 문서/저장소 자산, Wikimedia Commons, Unsplash/Pexels 등
   재사용이 허용된 것만. `WebSearch`로 찾고 `WebFetch`로 출처를 확인한다.
   **저작권이 명백한 이미지는 쓰지 않는다.**

웹 이미지를 쓸 때는 **볼트 폴더 안에 내려받아 상대 경로로 참조**한다 (핫링크는
나중에 깨진다):

```bash
curl -L -o "{볼트폴더}/assets/{파일명}.png" "{이미지 URL}"
```

모든 그림은 캡션과 출처를 함께 붙인다:

```html
<figure>
  <img src="assets/architecture.png" alt="요청 처리 흐름도" loading="lazy">
  <figcaption>그림 1. 요청 처리 흐름 — 출처: <a href="원본링크" rel="nofollow">출처명</a></figcaption>
</figure>
```

직접 그린 SVG면 `출처: 직접 작성`으로 표기한다. 쓸 만한 이미지를 못 찾겠으면
**저작권 위반 이미지로 때우지 말고 SVG를 직접 그린다.**

### 6. HTML 렌더

`references/html-template.md`의 템플릿을 쓴다. 요건:

- `<!DOCTYPE html>` … `<html lang="ko">` 로 시작하는 **완전한 단일 파일**
- CSS는 인라인, **CDN·외부 폰트·외부 스크립트 금지** — Obsidian은 오프라인에서
  열리고, 외부 링크는 언젠가 깨진다. 코드 하이라이팅도 최소한의 인라인 CSS로.
- 이미지는 상대 경로(`assets/…`) 또는 인라인 SVG/`data:` URI
- 라이트·다크 모드 모두에서 읽히게 (`color-scheme` + `prefers-color-scheme`)
- 시맨틱 마크업, `word-break: keep-all` (한국어 줄바꿈)

파일은 먼저 스크래치패드에 쓴다: `{scratchpad}/{제목}/index.html`
(+ 필요하면 `{scratchpad}/{제목}/assets/`).

### 7. 저장 — `obs` 스킬에 위임

`Skill` 툴로 **`obs`** 를 호출한다. 인자에 폴더 힌트와 제목을 넘기고, 첨부로
방금 만든 `index.html`(과 `assets/`)을 함께 저장하게 한다.

```
Skill(skill="obs", args='Documents/ "{제목}"')
```

- 폴더는 `obs`의 자동 라우팅 규칙을 따른다. 애매하면 인자 없이 넘겨 라우팅을 맡긴다.
  (개념/가이드 → `Documents/`, 기술 조사 → `Research/`, 특정 프로젝트 분석 →
  `Projects/`, 논문 → `Paper/`)
- `obs`는 `{폴더}/{제목}/{제목}.md`(folder-note)를 만들고 같은 폴더에 첨부를 둔다.
  **`.md` 노트는 반드시 함께 생성되어야 한다** — 본문에 요약 3~5줄을 담고
  `[[index.html]]`로 HTML을 링크한다.
- `obs`가 `Home.md` 인덱스까지 갱신한다.

### 8. 완료 보고

한국어로, 저장 경로 · 분량 · 그림 개수 · Obsidian 열기 링크를 알려준다.

```
✓ HTML 문서를 작성해 Obsidian에 저장했습니다.
  경로: Documents/{제목}/index.html
  노트: Documents/{제목}/{제목}.md
  분량: 약 {N}자 · 그림 {M}개
  열기: obsidian://open?vault={vault 이름}&file={URL인코딩된 경로}
```

---

## 스타일

- 인터뷰와 개요 확인은 **빠르게** 끝내고, 리서치·집필·작도는 알아서 진행한다.
  문단마다 사용자에게 되묻지 않는다.
- 처음부터 끝까지 사용자와는 한국어로 대화한다.
