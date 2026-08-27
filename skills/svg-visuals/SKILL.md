---
name: svg-visuals
description: >-
  Design system and layout rules for hand-drawn inline SVG diagrams that explain
  a concept inside a Korean HTML document. Read this before drawing any diagram
  for obs-html, obs-ppt, or tech-blog-writer — it fixes the palette, typography,
  spacing, and per-type layout math so every figure across the vault looks like
  one system. Covers six diagram types (flow, architecture, sequence,
  comparison, hierarchy, state), light/dark handling, and the Korean text-width
  rules that keep labels from overflowing their boxes. Use also when the user
  directly asks for a diagram, 도식, 구조도, 흐름도, or "이거 그림으로 그려줘".
  For numeric charts read the `dataviz` skill instead.
---

# svg-visuals — 설명용 인라인 SVG 디자인 시스템

문서 안에서 **개념을 설명하는 그림**을 그릴 때의 규칙이다. 목표는 예쁜 그림이
아니라 **읽으면 이해되는 그림**이고, 볼트 전체의 그림이 한 시스템처럼 보이는
것이다.

이 파일은 영어로 쓰여 있지만 **그림 안의 모든 텍스트와 캡션은 한국어**로 쓴다.
코드·식별자·정착된 기술 용어(`POST /users`, cache, deploy)는 그대로 둔다.

## 절대 규칙

1. **그림이 본문을 반복하면 그리지 않는다.** 그림은 글로 쓰면 장황해지는 것 —
   구조, 순서, 관계, 대조 — 만 맡는다. 판단 기준은 아래 "그릴 가치가 있는가".
2. **팔레트와 타이포를 임의로 바꾸지 않는다.** `references/design-tokens.md`의
   값을 그대로 쓴다. 강조색은 그림 하나당 **한 곳**에만.
3. **한글은 영문보다 넓다.** 박스 폭을 눈대중으로 정하지 말고
   `references/korean-text.md`의 산식으로 계산한다. 텍스트가 박스를 넘치는
   그림은 실패한 그림이다.
4. **외부 의존 금지.** 외부 폰트·이미지·스크립트를 참조하지 않는다. SVG 하나가
   그 자체로 완결되어야 Obsidian에서 오프라인으로 열린다.
5. **라이트·다크 양쪽에서 읽혀야 한다.** 색을 하드코딩하지 말고
   `currentColor`와 CSS 변수를 쓴다 (3단계).

---

## 워크플로

```
1. 그릴 가치 판단  →  2. 타입 선택  →  3. 토큰 적용
   →  4. 레이아웃 계산  →  5. 작도  →  6. 검수
```

### 1. 그릴 가치가 있는가

그림 하나를 그리기 전에 **한 문장으로 답한다: "이 그림은 무엇을 보여주는가?"**

답이 아래에 해당하면 그린다.

- **구조** — 무엇이 무엇 안에 있고 무엇과 연결되는가
- **순서** — 무엇이 먼저 일어나고 무엇이 그다음인가
- **관계** — 누가 누구를 호출하고 데이터가 어디로 흐르는가
- **대조** — A와 B가 어디서 갈리는가
- **변화** — 어떤 조건에서 어떤 상태로 넘어가는가

답이 "본문 내용을 요약한다"거나 "섹션이 허전해서"라면 **그리지 않는다.** 대신
본문을 다듬는다. 억지로 넣은 그림은 없느니만 못하다.

목록·정의·2~3줄짜리 설명은 그림이 아니라 **표나 본문**이 맞다.

### 2. 타입 선택

한 문장 답을 아래 6종에 대응시킨다. 각 타입의 레이아웃 규칙과 완성 예제는
`references/diagram-types.md`에 있다 — **고른 타입의 절만 읽는다.**

| 답이 이러면 | 타입 | 대표 쓰임 |
|---|---|---|
| "A 다음 B, 조건에 따라 갈림" | `flow` | 처리 흐름, 의사결정, 파이프라인 |
| "이런 조각들로 이루어져 있다" | `architecture` | 시스템 구성, 레이어, 모듈 경계 |
| "누가 누구를 언제 호출한다" | `sequence` | API 호출, 프로토콜, 시간축 상호작용 |
| "A와 B가 여기서 다르다" | `comparison` | 이전/이후, 대안 비교, 트레이드오프 |
| "이 아래에 이런 것들이 달린다" | `hierarchy` | 트리, 분류 체계, 디렉터리 |
| "이 조건이면 저 상태로 간다" | `state` | 상태 머신, 생명주기, 세션 전이 |

어디에도 안 맞으면 **가장 가까운 것을 골라 변형한다.** 새 타입을 즉흥으로
만들지 않는다.

### 3. 토큰 적용

`references/design-tokens.md`를 읽고 그 안의 `<style>` 블록을 SVG 안에
그대로 붙인다. 색·글꼴·선 굵기·반경이 전부 거기 정의돼 있다.

핵심만:

- **채우기**는 `var(--d-surface)`, **선**은 `var(--d-line)`, **글자**는
  `var(--d-fg)`. 색을 직접 쓰지 않는다.
- **강조색**(`var(--d-accent)`)은 그림당 한 곳. 핵심 경로나 결론 노드에만.
- 라이트·다크는 SVG 안 `@media (prefers-color-scheme: dark)`가 처리한다.

### 4. 레이아웃 계산

`references/korean-text.md`의 산식으로 **모든 박스 폭을 먼저 계산**한 뒤에
좌표를 잡는다. 그리고 나서 고치면 전부 다시 그려야 한다.

공통 규격:

- 캔버스 폭 **760** (본문 폭에 맞음), 높이는 내용에 따라
- `viewBox="0 0 760 {H}"` + `width="100%"` + `style="height:auto"` — 반응형.
  `height`는 **속성이 아니라 CSS로** 준다. `height="auto"`는 무효라 브라우저가
  기본 높이 150px로 렌더해 그림이 뭉개진다.
- 요소 간 최소 간격 **24**, 캔버스 안쪽 여백 **16**
- 박스 높이 기본 **48** (한 줄), **68** (두 줄)

### 5. 작도

```html
<figure>
  <svg viewBox="0 0 760 320" width="100%" style="height:auto"
       role="img" aria-labelledby="fig1-title">
    <title id="fig1-title">요청 처리 흐름</title>
    <style>/* design-tokens.md의 블록 */</style>
    <!-- 도형 -->
  </svg>
  <figcaption>그림 1. 요청 처리 흐름 — 출처: 직접 작성</figcaption>
</figure>
```

- `<title>`은 **필수**. 스크린 리더와 Obsidian 검색이 이걸 읽는다.
- `id`는 문서 안에서 유일해야 한다 (`fig1-`, `fig2-` … 접두사).
- 캡션은 `그림 {N}. {한 문장 설명} — 출처: 직접 작성` 형식.

### 6. 검수 — 저장 전에 반드시

아래를 **하나씩 눈으로 확인**한다. 하나라도 걸리면 고친다.

- [ ] 가장 긴 라벨이 박스 안에 여백을 두고 들어가는가 (산식 재확인)
- [ ] 그림만 보고도 무엇을 말하는지 알 수 있는가
- [ ] 강조색이 한 곳에만 쓰였는가
- [ ] 하드코딩된 색(`#`으로 시작하는 값)이 `<style>` 밖에 남아 있지 않은가
- [ ] 다크 모드에서 대비가 무너지지 않는가 (변수만 썼으면 자동 통과)
- [ ] `<title>`이 있고 `id`가 문서 안에서 유일한가
- [ ] 화살표가 겹치거나 도형을 관통하지 않는가
- [ ] 화살표 라벨 뒤 배경 사각형이 글자보다 넓은가 (선이 비치면 좁은 것)
- [ ] 그룹 테두리 오른쪽이 비어 보이지 않는가 (내용에 맞춰 폭을 줄였는가)

---

## 참조 파일

필요한 것만 읽는다. 전부 읽지 않는다.

| 파일 | 언제 읽는가 |
|---|---|
| `references/design-tokens.md` | 그림 그릴 때 **항상** — 팔레트·타이포·`<style>` 블록 |
| `references/korean-text.md` | 박스에 한글 라벨이 들어갈 때 **항상** — 폭 산식 |
| `references/diagram-types.md` | 타입 선택 후 **해당 절만** — 레이아웃 규칙 + 완성 예제 |

수치 비교 차트는 이 스킬이 아니라 **`dataviz` 스킬**을 읽는다.
