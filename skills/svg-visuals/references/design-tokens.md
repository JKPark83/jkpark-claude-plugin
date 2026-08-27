# design-tokens — 팔레트 · 타이포 · 규격

모든 그림이 공유하는 값이다. **이 파일의 `<style>` 블록을 SVG 안에 그대로
복사해 쓴다.** 값을 임의로 바꾸면 볼트 안 그림들의 톤이 갈린다.

## 붙여넣을 `<style>` 블록

```html
<style>
  /* svg-visuals design tokens — do not edit per-figure */
  svg {
    --d-fg:      #1c2024;  /* primary text */
    --d-muted:   #6f7780;  /* secondary text */
    --d-line:    #c4cbd4;  /* box borders, connectors */
    --d-surface: #fbfcfd;  /* box fill */
    --d-canvas:  #ffffff;  /* diagram background */
    --d-accent:  #2f6feb;  /* the one highlight per figure */
    --d-accent-fill: #eaf2ff; /* highlighted box fill */
    --d-shadow:  rgba(19, 26, 38, .10); /* soft depth, never a hard drop shadow */
    font-family: -apple-system, "Apple SD Gothic Neo", "Noto Sans KR",
                 system-ui, sans-serif;
  }
  @media (prefers-color-scheme: dark) {
    svg {
      --d-fg:      #e8eaed;
      --d-muted:   #9aa2ac;
      --d-line:    #4b535d;
      --d-surface: #242930;
      --d-canvas:  #1a1d21;
      --d-accent:  #6ea8fe;
      --d-accent-fill: #1d2e47;
      --d-shadow:  rgba(0, 0, 0, .34);
    }
  }
  .d-box   { fill: var(--d-surface); stroke: var(--d-line); stroke-width: 1.25;
             rx: 10; filter: url(#d-soft); }
  .d-box-a { fill: var(--d-accent-fill); stroke: var(--d-accent); stroke-width: 1.75;
             rx: 10; filter: url(#d-soft); }
  .d-group { fill: none; stroke: var(--d-line); stroke-width: 1.25;
             stroke-dasharray: 2 5; stroke-linecap: round; rx: 14; opacity: .75; }
  .d-line  { stroke: var(--d-line); stroke-width: 1.5; fill: none;
             stroke-linecap: round; }
  .d-line-a{ stroke: var(--d-accent); stroke-width: 2; fill: none;
             stroke-linecap: round; }
  .d-dash  { stroke: var(--d-line); stroke-width: 1.5; fill: none;
             stroke-dasharray: 5 5; stroke-linecap: round; }
  .d-t     { fill: var(--d-fg); font-size: 14px; letter-spacing: -.01em; }
  .d-t-sm  { fill: var(--d-muted); font-size: 12px; letter-spacing: -.005em; }
  .d-t-lg  { fill: var(--d-fg); font-size: 14px; font-weight: 600;
             letter-spacing: .04em; text-transform: none; }
  .d-t-code{ fill: var(--d-fg); font-size: 13px;
             font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
  .d-c     { text-anchor: middle; dominant-baseline: middle; }

  /* --- flow animation: connectors only, never nodes --- */
  .d-flow  { stroke: var(--d-accent); stroke-width: 2; fill: none;
             stroke-linecap: round; stroke-dasharray: 8 170;
             animation: d-move 3.2s linear infinite; opacity: .9; }
  .d-flow-2{ animation-delay: .5s; }
  .d-flow-3{ animation-delay: 1s; }
  @keyframes d-move { to { stroke-dashoffset: -178; } }

  @media (prefers-reduced-motion: reduce) {
    .d-flow { animation: none; stroke-dasharray: none; opacity: .35; }
  }
</style>
<defs>
  <filter id="d-soft" x="-12%" y="-24%" width="124%" height="152%">
    <feDropShadow dx="0" dy="1.5" stdDeviation="2.5" flood-color="var(--d-shadow)"/>
  </filter>
  <marker id="d-arrow" viewBox="0 0 10 10" refX="9" refY="5"
          markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
    <path d="M0.5,1 L9,5 L0.5,9" fill="none" stroke="var(--d-line)"
          stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
  </marker>
  <marker id="d-arrow-a" viewBox="0 0 10 10" refX="9" refY="5"
          markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
    <path d="M0.5,1 L9,5 L0.5,9" fill="none" stroke="var(--d-accent)"
          stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
  </marker>
</defs>
```

`<defs>`의 marker `id`도 문서 안에서 유일해야 한다. 한 문서에 그림이 여럿이면
`d-arrow` → `fig2-arrow`처럼 접두사를 붙이고 `marker-end` 참조도 함께 바꾼다.

## 클래스 사용법

| 클래스 | 용도 |
|---|---|
| `d-box` | 기본 박스. 대부분의 노드 |
| `d-box-a` | **그림당 하나** — 핵심 노드나 결론 |
| `d-group` | 점선 테두리. 레이어·경계·묶음을 감쌀 때 |
| `d-line` | 연결선. 화살표는 `marker-end="url(#d-arrow)"` |
| `d-line-a` | 강조 경로. `marker-end="url(#d-arrow-a)"` |
| `d-dash` | 선택적·비동기·간접 연결 |
| `d-flow` | **흐름 애니메이션.** 강조 경로 위에 겹쳐 깔면 빛줄기가 흐른다 |
| `d-t` | 박스 안 기본 라벨 (14px) |
| `d-t-sm` | 화살표 위 설명, 부가 정보 (12px) |
| `d-t-lg` | 그룹 제목, 섹션 헤더 (14px, 굵게, 자간 넓게) |
| `d-t-code` | 식별자·경로·메서드명 (모노스페이스 13px) |
| `d-c` | 가운데 정렬. 박스 안 텍스트에 함께 붙인다 |

박스 안 라벨은 `class="d-t d-c"`로 쓰고 `x`는 박스 중심, `y`도 박스 중심에 둔다.
`dominant-baseline: middle`이 세로 정렬을 처리한다.

## 규격 (모든 타입 공통)

| 항목 | 값 |
|---|---|
| 캔버스 폭 | 760 |
| 안쪽 여백 | 16 |
| 요소 간 최소 간격 | 24 |
| 박스 높이 — 한 줄 | 48 |
| 박스 높이 — 두 줄 | 68 |
| 박스 모서리 반경 | 10 (그룹은 14) |
| 선 굵기 | 1.25 (연결선 1.5, 강조 2) |
| 화살표 여백 | 도형 경계에서 4 띄운다 |

두 줄 라벨은 `<text>` 안에 `<tspan x="{cx}" dy="-8">`와 `<tspan x="{cx}" dy="18">`
두 개를 넣는다. **세 줄은 쓰지 않는다** — 세 줄이 필요하면 라벨이 긴 것이므로
줄이거나 캡션으로 뺀다.

## 흐름 애니메이션 — `d-flow`

강조하고 싶은 **경로 하나**에만 건다. 원리는 간단하다: 같은 좌표에 선을 하나 더
겹쳐 깔고, 짧은 대시(`8 170`)를 `stroke-dashoffset`으로 밀어 빛줄기처럼 보이게
한다.

```html
<!-- 1) 바탕이 되는 정적 선을 먼저 그린다 -->
<line class="d-line-a" x1="170" y1="64" x2="210" y2="64"
      marker-end="url(#d-arrow-a)"/>
<!-- 2) 똑같은 좌표에 흐름 선을 겹친다. 화살표는 붙이지 않는다 -->
<line class="d-flow" x1="170" y1="64" x2="210" y2="64"/>
```

- **정적 선을 반드시 함께 그린다.** `d-flow`만 그리면 애니메이션이 꺼졌을 때
  선이 사라진다.
- **`d-flow`에는 `marker-end`를 붙이지 않는다.** 대시가 움직이면서 화살표가
  깜빡인다.
- 경로가 여럿이면 `d-flow-2`, `d-flow-3`을 함께 붙여 시차를 준다.
  `class="d-flow d-flow-2"`.
- 곡선이나 꺾은선은 `<line>` 대신 `<path>`에 같은 클래스를 쓴다. 이때 대시
  간격(`8 170`)이 경로 길이보다 짧으면 빛줄기가 여러 개 보이므로, 긴 경로에는
  `stroke-dasharray: 8 340`처럼 인라인으로 늘려준다.

**한 그림에 흐름 선은 3개까지.** 그 이상이면 시선이 분산돼 오히려 안 읽힌다.
데이터가 흐르지 않는 관계(포함, 상속, 비교)에는 쓰지 않는다.

`prefers-reduced-motion: reduce`가 켜진 환경에서는 토큰이 자동으로 애니메이션을
끄고 옅은 실선으로 남긴다. **이 규칙을 지우지 않는다.**

## 색과 효과를 쓰지 말아야 할 곳

- **의미 구분을 색에만 의존하지 않는다.** 다크 모드와 흑백 출력에서 무너진다.
  선 종류(실선/점선), 도형, 위치로 먼저 구분하고 색은 보조로만.
- 빨강·초록으로 성공/실패를 표현하지 않는다. 라벨로 쓴다.
- 그라디언트를 쓰지 않는다. 깊이는 토큰의 `d-soft` 그림자가 이미 준다.
- **그림자를 직접 만들지 않는다.** `d-box`/`d-box-a`에 이미 걸려 있다.
  선이나 텍스트에는 걸지 않는다 — 흐려져서 가독성만 떨어진다.
- **노드를 애니메이션하지 않는다.** 박스가 깜빡이거나 움직이면 글을 읽을 수
  없다. 움직이는 것은 연결선뿐이다.
