# Translation & style guide

Read this before writing the post (SKILL.md step 4). Goal: a post that reads as
if a thoughtful Korean engineer wrote it from scratch — not a machine
translation, not a textbook.

## Natural Korean translation (avoid 번역투)

Translate the **meaning**, not word-for-word. The English structure should
disappear.

| 어색함 (번역투) | 자연스러움 |
| --- | --- |
| "이것은 당신이 캐시를 사용하는 것을 허락합니다." | "이렇게 하면 캐시를 쓸 수 있습니다." |
| "우리는 성능을 향상시킬 수 있는 능력을 가지고 있습니다." | "성능을 끌어올릴 수 있습니다." |
| "당신의 애플리케이션은 더 빠르게 될 것입니다." | "앱이 더 빨라집니다." |
| "이 함수는 데이터를 반환하는 것을 담당합니다." | "이 함수가 데이터를 반환합니다." |
| "그것은 매우 중요한 것입니다." | "이게 핵심입니다." |

Rules of thumb:

- **Drop redundant pronouns.** 영어의 "you / we / it / this"를 기계적으로
  옮기지 말 것. 한국어는 주어를 자주 생략한다.
- **Kill 무생물 주어 + ~를 가능하게 하다 / ~를 허용하다.** "X allows you to Y"
  → "X로 Y할 수 있다 / X를 쓰면 Y가 된다".
- **Prefer verbs over noun stacks.** "성능의 향상" → "성능을 높이다".
- **One idea per sentence.** 영어의 긴 관계절은 끊어서 두 문장으로.
- Read it aloud in your head — if a Korean dev wouldn't say it that way, rewrite.

## Terminology — when to keep English

- **Keep as-is** (code-facing, no clean Korean): `commit`, `merge`, `deploy`,
  `build`, `cache`, `props`, `state`, `hook`, `endpoint`, `payload`. 영문 그대로
  쓰거나 한글 음차(커밋, 머지, 배포, 캐시)를 쓰되 글 전체에서 일관되게.
- **Translate** when a natural, common Korean term exists: "concurrency" → 동시성,
  "latency" → 지연 시간, "throughput" → 처리량, "race condition" → 경쟁 조건.
- **First mention** of a non-obvious term: give Korean + English once —
  "서버 컴포넌트(Server Components)" — then use one form consistently after.
- Never invent a clumsy Korean word for a term everyone says in English.

## Writing for a junior developer

The reader can code and knows the basics. Calibrate to that:

- **Explain the "why" before the "how."** Junior devs can copy code; they
  struggle with *when* and *why* to use it. Lead with the problem it solves.
- **Define jargon on first use,** in one clause. Don't assume they know
  "idempotent", "memoization", "back-pressure".
- **Use analogies** for abstract ideas ("캐시는 자주 꺼내 쓰는 물건을 책상 위에
  올려두는 것과 같다").
- **Don't over-explain basics** — what a variable, loop, or function is. That
  insults the reader and pads the post.
- **Show, then tell.** A short runnable code snippet beats three paragraphs.
  Annotate code with brief Korean comments where a step is non-obvious.
- **Call out gotchas** explicitly — the bugs and surprises a junior will hit.

## Tone & formatting

- Default to **합니다체** (담백하고 정중한 기술 블로그 톤). 사용자가 해요체나
  반말 톤을 원하면 맞춘다. 한 글 안에서 문체를 섞지 말 것.
- Friendly and clear, not stiff or academic. Guide the reader, don't lecture.
- Short paragraphs (2–4 sentences). Use headings, lists, and code blocks to make
  the post scannable.
- Open with a hook (a real problem or question), close with a TL;DR the reader
  can walk away with.
- Korean spacing/맞춤법을 지킨다. 코드·명령어·파일명은 인라인 코드로 표시.
