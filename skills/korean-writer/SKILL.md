---
name: korean-writer
description: >-
  Use when producing Korean prose meant for a human reader — translating English
  source material into Korean, or writing Korean from scratch — so the result
  reads like a Korean article or blog post rather than a translation. Enforces
  three rules: never translate English literally, use the terms Korean articles
  and blogs actually use, and make every sentence understandable as Korean on
  its own. Triggers on "한국어로 번역해줘", "자연스럽게 번역해줘", "이 문서 한글로
  옮겨줘", "직역하지 말고", "블로그 톤으로 한국어로 써줘", "한국어로 정리해줘",
  "translate this into natural Korean", "korean-writer", "/korean-writer". Not
  for proofreading Korean that already exists (use the korean-reviewer agent),
  and not for machine-facing strings — code, identifiers, log messages, or CLI
  output.
---

# Korean Writer (korean-writer)

Produce Korean that a Korean reader experiences as **originally written in
Korean**. This covers two cases, and both follow the same rules:

- **Translation** — English source material into Korean.
- **Native writing** — Korean written from scratch, where English-shaped habits
  still creep in because the thinking happened in English.

## Language
- This SKILL.md is instructions for you (English). **The output document and all
  replies to the user are Korean.**

## The three rules

These are the whole point of the skill. Everything below is how to satisfy them.

1. **직역 금지.** Never map English word-for-word onto Korean. The English
   sentence structure must disappear entirely.
2. **한국어 기사·블로그의 용어로 옮긴다.** Use the word a Korean tech article or
   blog actually uses for that concept — not a literal rendering, not an
   invented Korean coinage.
3. **한국어만 읽고 뜻이 통해야 한다.** A reader who never sees the English must
   understand the sentence. If it only makes sense after mentally
   back-translating to English, it has failed.

## Method

Translate the **meaning**, not the words. Read the English, understand what it
says, then close it and write what a Korean writer would write to convey that.
Do not keep the source sentence in view while composing the Korean one — that
is where 직역 comes from.

Apply two tests to every sentence you produce:

- **소리 내어 읽기**: would a Korean developer actually say this to a colleague?
  If it reads like a written translation, rewrite it.
- **역번역**: if the phrase only makes sense once you translate it back to
  English, it is a calque. Replace it with what Korean actually uses.

## Rule 1 — 직역 금지

| 어색함 (직역) | 자연스러움 |
| --- | --- |
| 이것은 당신이 캐시를 사용하는 것을 허락합니다. | 이렇게 하면 캐시를 쓸 수 있습니다. |
| 우리는 성능을 향상시킬 수 있는 능력을 가지고 있습니다. | 성능을 끌어올릴 수 있습니다. |
| 당신의 애플리케이션은 더 빠르게 될 것입니다. | 앱이 더 빨라집니다. |
| 이 함수는 데이터를 반환하는 것을 담당합니다. | 이 함수가 데이터를 반환합니다. |
| 그것은 매우 중요한 것입니다. | 이게 핵심입니다. |
| 에러가 발생되어질 수 있습니다. | 에러가 날 수 있습니다. |

구조 차원에서 반드시 손볼 것:

- **대명사를 지운다.** 영어의 you / we / it / this / they를 기계적으로 옮기지
  않는다. 한국어는 주어와 목적어를 자주 생략한다.
- **무생물 주어 + ~를 가능하게 하다 / ~를 허용하다를 없앤다.** "X allows you to
  Y" → "X로 Y할 수 있다", "X를 쓰면 Y가 된다".
- **수동태를 능동으로.** "~에 의해 ~되어진다" 같은 이중 수동은 특히 어색하다.
- **명사 쌓기를 동사로 푼다.** "성능의 향상" → "성능을 높인다".
- **긴 관계절은 끊는다.** 한 문장에 한 가지 생각. 영어의 which/that 절은 대개
  한국어에서 별도 문장이 된다.
- **불필요한 ~들을 뺀다.** 수가 문맥에서 분명하면 복수 표시는 군더더기다.
  "사용자들은 설정들을 변경할 수 있습니다" → "사용자는 설정을 바꿀 수 있다".
- **~하는 것 남발을 줄인다.** "로그를 확인하는 것이 중요합니다" → "로그를 꼭
  확인해야 합니다".
- **만약, ~에도 불구하고 같은 접속 군더더기를 정리한다.** "만약 ~라면" → "~라면",
  "~에도 불구하고" → "~인데도", "~지만".

## Rule 2 — 한국어 기사·블로그의 용어

한국어 기술 글이 실제로 쓰는 말을 고른다. 판단 순서는 이렇다.

1. **한국어 정착 용어가 있으면 그걸 쓴다.** concurrency → 동시성,
   latency → 지연 시간, throughput → 처리량, race condition → 경쟁 조건,
   threshold → 임계값, deprecated → 지원 중단.
2. **영어(또는 음차)가 표준이면 그대로 둔다.** commit, merge, deploy, build,
   cache, props, state, hook, endpoint, payload — 억지로 한국어로 바꾸지 않는다.
   커밋, 머지, 배포, 캐시처럼 음차를 쓰되 글 전체에서 하나로 통일한다.
3. **처음 나오는 낯선 용어는 한 번만 병기한다.** "서버 컴포넌트(Server
   Components)" — 이후로는 한 형태만 쓴다.
4. **한국어에 없는 말을 지어내지 않는다.** 이게 가장 흔한 실패다. 아래 참고.

### 지어낸 말 대신 뜻을 쓴다

영어 비유를 한국어 단어로 옮기면 한국 개발자가 실제로 쓰지 않는 말이 된다.
동사뿐 아니라 **명사**도 확인한다. 명사 비유는 평범한 합성어처럼 보여서 더 잘
숨는다.

| 지어낸 말 | 실제 쓰는 말 |
| --- | --- |
| 배선되어 있다 (wired up) | 연결되어 있다 |
| 구워져 있다 (baked in) | 내장되어 있다, 고정되어 있다 |
| 표면화한다 (surfaces X) | 드러낸다, 보여준다 |
| 수화한다 (hydrates) | 초기 데이터를 채워 넣는다 |
| 우산형 스킬 (umbrella skill) | 여러 용도를 묶은 스킬 |
| 배관 (plumbing) | 연결 작업, 이어 붙이는 작업 |
| 지문 (fingerprint) | 식별값 |
| 발자국 (footprint) | 차지하는 용량 |
| 은탄환 (silver bullet) | 만능 해결책 |
| 천장을 친다 (hit the ceiling) | 한계에 부딪힌다 |
| 공을 굴린다 (get the ball rolling) | 첫발을 뗀다, 시작한다 |
| 테이블 위에 올려놓는다 (put on the table) | 검토 대상으로 삼는다 |

두 가지를 더 본다.

- **한국어 문장 안에 영어 단어를 날것으로 남기지 않는다.** "관측 seam 보유"처럼
  독자가 모르는 영어 명사를 그대로 끼워 넣지 말고, 번역하거나("관측 지점")
  문장을 다시 써서 하는 일을 설명한다. props, deploy, cache처럼 이미 표준인
  용어만 영어로 둔다.
- **문서 전체에서 용어를 통일한다.** 같은 개념을 앞에서는 "임계값", 뒤에서는
  "문턱값"이라고 부르면 둘 다 뜻이 통해도 결함이다.

## Rule 3 — 한국어만 읽고 뜻이 통할 것

원문을 못 본 독자를 기준으로 판단한다.

- **문장이 무엇을 말하는지 한 번에 잡히는가.** 두 번 읽어야 하면 끊거나 다시
  쓴다.
- **영어를 떠올려야 이해되는 표현은 실패다.** 역번역 테스트에 걸리면 뜻을 직접
  풀어 쓴다.
- **원문이 모호하면 옮기면서 명확하게 만든다.** 영어의 애매한 대명사나 생략된
  주어는 한국어에서 무엇을 가리키는지 밝혀 준다.
- **문화적 전제가 깔린 비유는 대체한다.** 야구·미식축구 비유처럼 한국 독자에게
  안 통하는 것은 같은 뜻의 다른 표현으로 바꾼다.
- **뜻을 바꾸지는 않는다.** 자연스럽게 만드는 것과 내용을 손대는 것은 다르다.
  사실, 숫자, 논리, 고유명사는 그대로 둔다.

## 문체

- 기본은 **합니다체**. 사용자가 해요체나 반말, ~한다체를 원하면 맞춘다. 한 문서
  안에서 문체를 섞지 않는다.
- 문단은 짧게(2~4문장). 제목, 목록, 코드 블록으로 훑어보기 좋게 만든다.
- 한국어 띄어쓰기와 맞춤법을 지킨다. 코드·명령어·파일명은 인라인 코드로 표시한다.
- 딱딱한 관공서 말투(~함에 있어, ~를 위하여, 상기, 당해)를 쓰지 않는다.

## 건드리지 않는 것

- 코드 블록, 명령어, 식별자, 파일 경로, URL.
- Markdown/HTML 문법, 태그, 링크, 이미지.
- 원문의 사실, 숫자, 논리, 고유명사.

## 절차

1. 입력을 확보한다. 파일 경로를 받으면 `Read`, 인라인 텍스트를 받으면 그대로
   쓴다. 웹 문서면 가져와서 본문만 추린다.
2. 출력 형태를 확인한다 — 새 파일로 저장할지, 기존 파일을 고칠지, 대화로 보여줄
   지. 불분명하면 대화로 보여주고 저장 여부를 묻는다.
3. 문단 단위로 뜻을 파악한 뒤 한국어로 다시 쓴다. 원문 문장을 옆에 두고 한 줄씩
   대응시키지 않는다.
4. **검수 패스**: 다 쓴 뒤 원문 없이 결과물만 처음부터 읽는다. 소리 내어 읽기와
   역번역 테스트를 문장마다 적용하고, 용어가 문서 전체에서 통일됐는지 확인한다.
   고칠 것이 없을 때까지 반복한다.
5. 결과를 전달한다. 파일로 저장했으면 경로를 알려 준다. 번역하면서 판단이
   갈렸던 용어가 있으면 두세 줄로 짚어 준다.

## 이미 있는 한국어를 고치는 경우

이 스킬은 **새로 쓰는** 쪽이다. 사용자가 이미 작성된 한국어 문서를 다듬어
달라고 하면 `korean-reviewer` 에이전트를 쓴다. 그쪽은 파일을 직접 수정하고 수정
내역을 표로 돌려준다.
