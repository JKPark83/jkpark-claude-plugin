# design-tokens — 팔레트 · 타이포 · 규격

모든 그림이 공유하는 값이다. **이 파일의 `<style>` 블록을 SVG 안에 그대로
복사해 쓴다.** 값을 임의로 바꾸면 볼트 안 그림들의 톤이 갈린다.

## 붙여넣을 `<style>` 블록

```html
<style>
  /* svg-visuals design tokens — do not edit per-figure */
  svg {
    --d-fg:      #24292f;  /* primary text */
    --d-muted:   #6b7280;  /* secondary text, captions inside the figure */
    --d-line:    #b8c0cc;  /* box borders, connectors */
    --d-surface: #f6f8fa;  /* box fill */
    --d-canvas:  #ffffff;  /* diagram background */
    --d-accent:  #0969da;  /* the one highlight per figure */
    --d-accent-fill: #ddf0ff; /* highlighted box fill */
    font-family: -apple-system, "Apple SD Gothic Neo", "Noto Sans KR",
                 system-ui, sans-serif;
  }
  @media (prefers-color-scheme: dark) {
    svg {
      --d-fg:      #e6e6e6;
      --d-muted:   #9aa0a6;
      --d-line:    #4a5158;
      --d-surface: #262b31;
      --d-canvas:  #1e1e1e;
      --d-accent:  #6cb6ff;
      --d-accent-fill: #1c3049;
    }
  }
  .d-box   { fill: var(--d-surface); stroke: var(--d-line); stroke-width: 1.5; rx: 6; }
  .d-box-a { fill: var(--d-accent-fill); stroke: var(--d-accent); stroke-width: 2; rx: 6; }
  .d-group { fill: none; stroke: var(--d-line); stroke-width: 1.5;
             stroke-dasharray: 5 4; rx: 8; }
  .d-line  { stroke: var(--d-line); stroke-width: 1.5; fill: none; }
  .d-line-a{ stroke: var(--d-accent); stroke-width: 2; fill: none; }
  .d-dash  { stroke: var(--d-line); stroke-width: 1.5; fill: none;
             stroke-dasharray: 5 4; }
  .d-t     { fill: var(--d-fg); font-size: 14px; }
  .d-t-sm  { fill: var(--d-muted); font-size: 12px; }
  .d-t-lg  { fill: var(--d-fg); font-size: 15px; font-weight: 600; }
  .d-t-code{ fill: var(--d-fg); font-size: 13px;
             font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
  .d-c     { text-anchor: middle; dominant-baseline: middle; }
</style>
<defs>
  <marker id="d-arrow" viewBox="0 0 10 10" refX="9" refY="5"
          markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 z" fill="var(--d-line)"/>
  </marker>
  <marker id="d-arrow-a" viewBox="0 0 10 10" refX="9" refY="5"
          markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 z" fill="var(--d-accent)"/>
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
| `d-t` | 박스 안 기본 라벨 (14px) |
| `d-t-sm` | 화살표 위 설명, 부가 정보 (12px) |
| `d-t-lg` | 그룹 제목, 섹션 헤더 (15px, 굵게) |
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
| 박스 모서리 반경 | 6 (그룹은 8) |
| 선 굵기 | 1.5 (강조 2) |
| 화살표 여백 | 도형 경계에서 4 띄운다 |

두 줄 라벨은 `<text>` 안에 `<tspan x="{cx}" dy="-8">`와 `<tspan x="{cx}" dy="18">`
두 개를 넣는다. **세 줄은 쓰지 않는다** — 세 줄이 필요하면 라벨이 긴 것이므로
줄이거나 캡션으로 뺀다.

## 색을 쓰지 말아야 할 곳

- **의미 구분을 색에만 의존하지 않는다.** 다크 모드와 흑백 출력에서 무너진다.
  선 종류(실선/점선), 도형, 위치로 먼저 구분하고 색은 보조로만.
- 빨강·초록으로 성공/실패를 표현하지 않는다. 라벨로 쓴다.
- 그라디언트·그림자·투명도를 쓰지 않는다. 평면으로 그린다.
