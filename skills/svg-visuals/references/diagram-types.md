# diagram-types — 6종 레이아웃 규칙과 예제

**고른 타입의 절만 읽는다.** 각 절은 레이아웃 계산 → 완성 예제 순서다.
예제의 `<style>`/`<defs>`는 지면상 생략했다 — `design-tokens.md`의 블록을
그대로 넣는다. 모든 예제는 캔버스 폭 760 기준이다.

---

## flow — 흐름도

**쓸 때**: 처리 순서, 의사결정 분기, 파이프라인 단계.

### 레이아웃

- 단계 4개 이하면 **가로**, 5개 이상이거나 분기가 있으면 **세로**.
- 가로: 박스 폭 `W`, 간격 `g = (760 - 32 - N×W) / (N-1)`. `g < 24`가 되면
  세로로 바꾼다.
- 세로: 박스를 `x=290` 중심(폭 180 기준)에 세우고 세로 간격 **32**.
- 분기는 마름모(`<polygon>`)로 쓰고, 갈래 라벨은 화살표 위 `d-t-sm`.
- 되돌아가는 화살표는 옆으로 빼서 `d-dash`로 그린다. 도형을 관통시키지 않는다.

### 예제 — 가로 4단계 + 분기

```html
<figure>
<svg viewBox="0 0 760 300" width="100%" style="height:auto"
     role="img" aria-labelledby="fig1-title">
  <title id="fig1-title">요청 처리 흐름</title>
  <!-- design-tokens.md의 <style>과 <defs>를 여기에 -->

  <rect class="d-box" x="16"  y="40" width="150" height="48"/>
  <text class="d-t d-c" x="91"  y="64">요청 수신</text>

  <rect class="d-box" x="214" y="40" width="150" height="48"/>
  <text class="d-t d-c" x="289" y="64">인증 확인</text>

  <polygon class="d-box" points="487,34 567,64 487,94 407,64"/>
  <text class="d-t d-c" x="487" y="64">유효한가</text>

  <rect class="d-box-a" x="610" y="40" width="134" height="48"/>
  <text class="d-t d-c" x="677" y="64">처리 완료</text>

  <rect class="d-box" x="407" y="200" width="160" height="48"/>
  <text class="d-t d-c" x="487" y="224">401 응답</text>

  <line class="d-line" x1="170" y1="64" x2="210" y2="64" marker-end="url(#d-arrow)"/>
  <line class="d-line" x1="368" y1="64" x2="403" y2="64" marker-end="url(#d-arrow)"/>
  <line class="d-line-a" x1="571" y1="64" x2="606" y2="64" marker-end="url(#d-arrow-a)"/>
  <line class="d-flow" x1="571" y1="64" x2="606" y2="64"/>
  <line class="d-line" x1="487" y1="98" x2="487" y2="196" marker-end="url(#d-arrow)"/>

  <rect x="580" y="46" width="20" height="16" fill="var(--d-canvas)"/>
  <text class="d-t-sm d-c" x="590" y="54">예</text>
  <rect x="465" y="139" width="44" height="16" fill="var(--d-canvas)"/>
  <text class="d-t-sm d-c" x="487" y="147">아니오</text>
</svg>
<figcaption>그림 1. 요청 처리 흐름 — 출처: 직접 작성</figcaption>
</figure>
```

---

## architecture — 구성도

**쓸 때**: 시스템 구성 요소, 레이어, 모듈 경계.

### 레이아웃

- **레이어는 가로 띠**로 쌓는다. 위가 사용자에 가깝고 아래가 저장소.
- 각 레이어는 `d-group`(점선)으로 감싸고 왼쪽 위에 `d-t-lg` 제목.
- 레이어 안 박스는 균등 분배: 박스 폭 `W = (그룹폭 - 32 - (n-1)×24) / n`.
- 레이어 높이 = 박스 높이 + **56** (제목 28 + 위아래 여백).
- 레이어 간 간격 **28**. 레이어를 가로지르는 호출은 세로 화살표.
- **그룹 폭은 내용에 맞춘다.** 박스 2개짜리 레이어를 728로 늘리면 오른쪽이
  텅 빈다. 그룹 폭 = `마지막 박스 오른쪽 끝 + 16`.
- 그룹 제목(`d-t-lg`)과 첫 박스 사이를 **8** 띄운다. 제목 baseline은 그룹
  상단 + 24, 첫 박스 상단은 그룹 상단 + 32.
- **한 레이어에 박스 4개 이하.** 넘으면 묶어서 이름을 붙인다.

### 예제 — 3레이어

```html
<figure>
<svg viewBox="0 0 760 356" width="100%" style="height:auto"
     role="img" aria-labelledby="fig2-title">
  <title id="fig2-title">서비스 구성</title>
  <!-- design-tokens.md의 <style>과 <defs>를 여기에 -->

  <rect class="d-group" x="16" y="16" width="496" height="92"/>
  <text class="d-t-lg" x="32" y="40">클라이언트</text>
  <rect class="d-box" x="32"  y="48" width="220" height="48"/>
  <text class="d-t d-c" x="142" y="72">웹 앱</text>
  <rect class="d-box" x="276" y="48" width="220" height="48"/>
  <text class="d-t d-c" x="386" y="72">모바일 앱</text>

  <rect class="d-group" x="16" y="136" width="728" height="92"/>
  <text class="d-t-lg" x="32" y="160">API 계층</text>
  <rect class="d-box-a" x="32"  y="172" width="220" height="48"/>
  <text class="d-t d-c" x="142" y="196">게이트웨이</text>
  <rect class="d-box" x="276" y="172" width="220" height="48"/>
  <text class="d-t d-c" x="386" y="196">인증 서비스</text>
  <rect class="d-box" x="520" y="172" width="192" height="48"/>
  <text class="d-t d-c" x="616" y="196">주문 서비스</text>

  <rect class="d-group" x="16" y="256" width="496" height="92"/>
  <text class="d-t-lg" x="32" y="280">저장소</text>
  <rect class="d-box" x="32"  y="292" width="220" height="44"/>
  <text class="d-t-code d-c" x="142" y="314">PostgreSQL</text>
  <rect class="d-box" x="276" y="292" width="220" height="44"/>
  <text class="d-t-code d-c" x="386" y="314">Redis</text>

  <line class="d-line" x1="142" y1="104" x2="142" y2="168" marker-end="url(#d-arrow)"/>
  <line class="d-flow" x1="142" y1="104" x2="142" y2="168"/>
  <line class="d-line" x1="386" y1="104" x2="386" y2="168" marker-end="url(#d-arrow)"/>
  <line class="d-line" x1="142" y1="224" x2="142" y2="288" marker-end="url(#d-arrow)"/>
  <line class="d-flow d-flow-2" x1="142" y1="224" x2="142" y2="288"/>
  <line class="d-dash" x1="386" y1="224" x2="386" y2="288" marker-end="url(#d-arrow)"/>
</svg>
<figcaption>그림 2. 서비스 구성 — 점선은 캐시 조회 — 출처: 직접 작성</figcaption>
</figure>
```

---

## sequence — 시퀀스

**쓸 때**: 시간 순서가 있는 상호작용. API 호출, 프로토콜, 핸드셰이크.

### 레이아웃

- 참여자를 **위쪽에 가로로** 놓고 각각 아래로 세로 생명선(`d-dash`).
- 참여자 간격 = `(760 - 32) / n`, 생명선 `x`는 각 구간 중심.
- 메시지는 생명선 사이 가로 화살표, 세로 간격 **40**.
- 메시지 라벨은 화살표 **위 6px**, `d-t-sm`. 응답은 `d-dash` + 화살표.
- **참여자 4명, 메시지 8개 이하.** 넘으면 구간을 나눠 그림 두 개로.

### 예제 — 참여자 3, 메시지 4

```html
<figure>
<svg viewBox="0 0 760 280" width="100%" style="height:auto"
     role="img" aria-labelledby="fig3-title">
  <title id="fig3-title">토큰 발급 순서</title>
  <!-- design-tokens.md의 <style>과 <defs>를 여기에 -->

  <rect class="d-box" x="46"  y="16" width="180" height="44"/>
  <text class="d-t d-c" x="136" y="38">클라이언트</text>
  <rect class="d-box" x="290" y="16" width="180" height="44"/>
  <text class="d-t d-c" x="380" y="38">게이트웨이</text>
  <rect class="d-box" x="534" y="16" width="180" height="44"/>
  <text class="d-t d-c" x="624" y="38">인증 서버</text>

  <line class="d-dash" x1="136" y1="60" x2="136" y2="256"/>
  <line class="d-dash" x1="380" y1="60" x2="380" y2="256"/>
  <line class="d-dash" x1="624" y1="60" x2="624" y2="256"/>

  <line class="d-line" x1="136" y1="100" x2="376" y2="100" marker-end="url(#d-arrow)"/>
  <text class="d-t-sm d-c" x="256" y="92">로그인 요청</text>

  <line class="d-line" x1="380" y1="140" x2="620" y2="140" marker-end="url(#d-arrow)"/>
  <text class="d-t-sm d-c" x="500" y="132">자격 검증</text>

  <line class="d-dash" x1="624" y1="180" x2="384" y2="180" marker-end="url(#d-arrow)"/>
  <text class="d-t-sm d-c" x="504" y="172">토큰 반환</text>

  <line class="d-line-a" x1="380" y1="220" x2="140" y2="220" marker-end="url(#d-arrow-a)"/>
  <line class="d-flow" x1="380" y1="220" x2="140" y2="220" stroke-dasharray="8 340"/>
  <text class="d-t-sm d-c" x="260" y="212">세션 쿠키</text>
</svg>
<figcaption>그림 3. 토큰 발급 순서 — 출처: 직접 작성</figcaption>
</figure>
```

---

## comparison — 비교 대조

**쓸 때**: 이전/이후, 대안 A와 B, 트레이드오프.

### 레이아웃

- **좌우 2단**. 각 단 폭 `(760 - 32 - 40) / 2 = 344`. 가운데 간격 40.
- 각 단 위에 `d-t-lg` 제목, 아래에 항목 박스를 세로로 쌓는다 (간격 16).
- **가운데 세로 구분선**(`d-line`)으로 대조를 시각화한다.
- 항목 수는 양쪽을 **맞춘다.** 한쪽이 적으면 빈칸을 두지 말고 항목을 합친다.
- 3단 이상은 이 타입이 아니라 **표**로 쓴다.

### 예제 — 2단 3항목

```html
<figure>
<svg viewBox="0 0 760 260" width="100%" style="height:auto"
     role="img" aria-labelledby="fig4-title">
  <title id="fig4-title">동기 방식과 큐 방식 비교</title>
  <!-- design-tokens.md의 <style>과 <defs>를 여기에 -->

  <text class="d-t-lg d-c" x="188" y="28">동기 호출</text>
  <text class="d-t-lg d-c" x="572" y="28">큐 경유</text>
  <line class="d-line" x1="380" y1="16" x2="380" y2="244"/>

  <rect class="d-box" x="16" y="48" width="344" height="48"/>
  <text class="d-t d-c" x="188" y="72">응답까지 대기</text>
  <rect class="d-box" x="16" y="112" width="344" height="48"/>
  <text class="d-t d-c" x="188" y="136">장애가 즉시 전파</text>
  <rect class="d-box" x="16" y="176" width="344" height="48"/>
  <text class="d-t d-c" x="188" y="200">구현이 단순</text>

  <rect class="d-box" x="400" y="48" width="344" height="48"/>
  <text class="d-t d-c" x="572" y="72">즉시 반환</text>
  <rect class="d-box-a" x="400" y="112" width="344" height="48"/>
  <text class="d-t d-c" x="572" y="136">장애가 격리됨</text>
  <rect class="d-box" x="400" y="176" width="344" height="48"/>
  <text class="d-t d-c" x="572" y="200">운영 부담 증가</text>
</svg>
<figcaption>그림 4. 동기 방식과 큐 방식 비교 — 출처: 직접 작성</figcaption>
</figure>
```

---

## hierarchy — 계층 · 트리

**쓸 때**: 분류 체계, 디렉터리 구조, 조직도, 상속 관계.

### 레이아웃

- 깊이 3 이하면 **위에서 아래**, 4 이상이면 **왼쪽에서 오른쪽**(들여쓰기형).
- 세로형: 레벨 간 간격 **64**, 같은 레벨 박스 간 간격 **24**.
- 부모에서 자식으로는 **직각 꺾은선**(`<path>`)으로 잇는다. 대각선 금지.
  ```
  M {부모cx} {부모하단} V {중간y} H {자식cx} V {자식상단}
  ```
  중간 `y` = 부모 하단 + 32.
- 형제가 5개를 넘으면 가로형으로 바꾸거나 묶어서 이름을 붙인다.

### 예제 — 깊이 3

```html
<figure>
<svg viewBox="0 0 760 260" width="100%" style="height:auto"
     role="img" aria-labelledby="fig5-title">
  <title id="fig5-title">설정 우선순위 구조</title>
  <!-- design-tokens.md의 <style>과 <defs>를 여기에 -->

  <rect class="d-box-a" x="300" y="16" width="160" height="48"/>
  <text class="d-t d-c" x="380" y="40">최종 설정</text>

  <rect class="d-box" x="120" y="128" width="160" height="48"/>
  <text class="d-t d-c" x="200" y="152">프로젝트 설정</text>
  <rect class="d-box" x="480" y="128" width="160" height="48"/>
  <text class="d-t d-c" x="560" y="152">사용자 설정</text>

  <rect class="d-box" x="40"  y="196" width="140" height="44"/>
  <text class="d-t-code d-c" x="110" y="218">.env</text>
  <rect class="d-box" x="204" y="196" width="140" height="44"/>
  <text class="d-t-code d-c" x="274" y="218">config.yaml</text>

  <path class="d-line" d="M380 64 V96 H200 V124" marker-end="url(#d-arrow)"/>
  <path class="d-line" d="M380 64 V96 H560 V124" marker-end="url(#d-arrow)"/>
  <path class="d-line" d="M200 176 V186 H110 V192" marker-end="url(#d-arrow)"/>
  <path class="d-line" d="M200 176 V186 H274 V192" marker-end="url(#d-arrow)"/>
</svg>
<figcaption>그림 5. 설정 우선순위 구조 — 아래가 위를 덮어쓴다 — 출처: 직접 작성</figcaption>
</figure>
```

---

## state — 상태 전이

**쓸 때**: 상태 머신, 생명주기, 세션·주문·작업 상태.

### 레이아웃

- 상태는 **모서리를 둥글게**(`rx="24"`) 해서 flow의 사각형과 구분한다.
- 상태 3~4개면 **가로 일렬**, 5개 이상이거나 순환하면 **원형 배치**.
- 전이 조건은 `d-t-sm`. **모든 화살표에 조건을 붙인다** — 조건 없는 전이는
  정보가 없다.
- **가로 배치에서는 라벨을 박스 위쪽(상태 박스 상단 - 12)에 놓는다.** 상태 간
  간격은 48뿐이라 라벨을 화살표 위에 겹치면 배경 사각형이 옆 박스를 덮는다.
  되돌아가는 전이만 우회선 위에 배경 사각형과 함께 놓는다.
- 되돌아가는 전이는 박스 **아래로 우회**시킨다. 시작 상태는 왼쪽 끝,
  종료 상태는 `d-box-a`.
- 자기 자신으로 도는 전이는 박스 위 반원 `<path>`.

### 예제 — 가로 4상태 + 되돌아감

```html
<figure>
<svg viewBox="0 0 760 176" width="100%" style="height:auto"
     role="img" aria-labelledby="fig6-title">
  <title id="fig6-title">작업 상태 전이</title>
  <!-- design-tokens.md의 <style>과 <defs>를 여기에 -->

  <rect class="d-box" x="16"  y="48" width="150" height="48" rx="24"/>
  <text class="d-t d-c" x="91"  y="72">대기</text>
  <rect class="d-box" x="214" y="48" width="150" height="48" rx="24"/>
  <text class="d-t d-c" x="289" y="72">실행 중</text>
  <rect class="d-box" x="412" y="48" width="150" height="48" rx="24"/>
  <text class="d-t d-c" x="487" y="72">검증</text>
  <rect class="d-box-a" x="610" y="48" width="134" height="48" rx="24"/>
  <text class="d-t d-c" x="677" y="72">완료</text>

  <line class="d-line" x1="170" y1="72" x2="210" y2="72" marker-end="url(#d-arrow)"/>
  <text class="d-t-sm d-c" x="190" y="36">워커 획득</text>

  <line class="d-line" x1="368" y1="72" x2="408" y2="72" marker-end="url(#d-arrow)"/>
  <text class="d-t-sm d-c" x="388" y="36">종료 코드 0</text>

  <line class="d-line-a" x1="566" y1="72" x2="606" y2="72" marker-end="url(#d-arrow-a)"/>
  <line class="d-flow" x1="566" y1="72" x2="606" y2="72"/>
  <text class="d-t-sm d-c" x="586" y="36">검증 통과</text>

  <path class="d-dash" d="M487 100 V152 H91 V100" marker-end="url(#d-arrow)"/>
  <rect x="267" y="144" width="44" height="16" fill="var(--d-canvas)"/>
  <text class="d-t-sm d-c" x="289" y="152">재시도</text>
</svg>
<figcaption>그림 6. 작업 상태 전이 — 점선은 실패 시 재시도 — 출처: 직접 작성</figcaption>
</figure>
```

---

## 공통 마무리

어떤 타입이든 그린 뒤 `SKILL.md`의 **6단계 검수 체크리스트**를 돌린다.
특히 **가장 긴 라벨의 폭 재확인**과 **강조색 한 곳** 두 가지가 가장 자주
어긋난다.
