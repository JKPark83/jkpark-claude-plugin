---
name: analyze-image
description: >-
  Default skill for analyzing an image the user wants you to look at, WITHOUT
  requiring them to mention the clipboard. Use whenever the user asks you to
  look at / read / explain / debug an image, screenshot, screen, UI, error, or
  diagram and there is no image attached to the message and no file path given —
  e.g. "이 이미지 분석해줘", "이미지 봐줘", "이 화면 뭔지 봐줘", "방금 캡쳐한 거
  봐바", "이 에러 화면 분석해줘", "이 다이어그램 설명해줘", "스크린샷 좀 봐줘",
  "analyze this image", "look at this screenshot", "what's on my screen". In
  these cases the image is almost always on the macOS clipboard, so this skill
  checks the clipboard FIRST and reads whatever screenshot/picture is there.
---

# Analyze Image (analyze-image)

The user wants you to look at an image, but **didn't attach a file and didn't
give a path** — on macOS the picture is almost always sitting on the
**clipboard** (they just hit ⌘⇧4 / ⌃⌘⇧4, or copied an image). So instead of
asking "where is the image?" or making them say the word "clipboard", this
skill **checks the clipboard first by default** and analyzes whatever is there.

## Language
- This SKILL.md is instructions for you (English). **Always reply to the user in Korean.**

## When to use this skill
Use it as the **default path** for any "look at / analyze this image" request
where the image source is unstated. Concretely:
- The user asks you to look at / read / explain / debug an image, screenshot,
  screen, UI, error, or diagram, **AND**
- No image is attached to the current message, **AND**
- No file path or URL to an image was given.

Do **NOT** use this skill (handle those directly instead) when:
- An image is already attached to the message → just read it.
- The user gave a file path or URL → Read / fetch that instead.
- The request is not about an image at all.

## Steps
1. Dump the clipboard image to a file:
   ```bash
   bash "$SKILL_DIR/grab-clipboard.sh"
   ```
   `$SKILL_DIR` = the absolute path of this skill's folder. Substitute the real
   path; never hardcode a different one.
2. Act on what the script prints:
   - **A file path** → use the **Read** tool on that path to view the image,
     then analyze it and answer the user's question in Korean.
   - **`ERR_NO_IMAGE`** → the clipboard has no image. In Korean, tell the user
     the clipboard is empty and ask them to either **capture a screenshot**
     (⌘⇧4 영역 / ⌃⌘⇧4 클립보드로 복사), **copy an image**, **attach the image to
     the message**, or **give a file path** — then try again.
3. Answer in Korean based on the image. If the user's intent is unclear, briefly
   describe what you see and ask what they specifically want to know (e.g.
   에러 원인 분석인지, UI 설명인지, 텍스트 추출인지).

## Notes
- **macOS only** (uses `osascript`; no extra install needed).
- One fixed temp file, overwritten on each run (any stale copy is cleared
  first), so nothing accumulates — always Read the path the script **just
  printed**, not a remembered one.
- If a screenshot was saved to a file (e.g. Desktop) rather than copied, the
  clipboard may be empty — that's the `ERR_NO_IMAGE` case; guide the user to
  copy it or give the path.
