# Animated status line (애니메이션 상태줄)

A drop-in [Claude Code status line](https://code.claude.com/docs/en/statusline)
with an **animated emoji mascot** that reacts to what Claude is doing:

| State | Emoji | Color | When |
|-------|-------|-------|------|
| **working** | 🤖 ↔ 🧠 (ping-pong) | orange | from your prompt until Claude finishes responding |
| **idle**    | 😴 ↔ 💤 (ping-pong) | blue   | while Claude waits for your next input |

The mascot slides across a small track and the line also shows
`dir | git branch+status | model | effort | context%` (Powerlevel10k-style).

> **Why this isn't auto-installed by the plugin:** Claude Code plugins
> **cannot** register a main `statusLine` — only the user's own
> `settings.json` can. So this ships as an opt-in script + config you copy in.

## How it works

- `claude-statusline.sh` reads `~/.claude/.statusline-mode` (`working` / `idle`)
  to pick which emoji set to animate, and advances a frame counter stored in
  `~/.claude/.statusline-anim-frame` on every invocation.
- Two **hooks** keep the mode file current: `UserPromptSubmit` writes
  `working`, `Stop` writes `idle`.
- `refreshInterval: 1` re-runs the status line every second so the animation
  keeps moving **even while idle** (without it, Claude Code only re-renders the
  status line on events, so an idle animation would freeze).

## Install

1. Copy the script into your Claude config dir and make it executable:

   ```bash
   cp statusline/claude-statusline.sh ~/.claude/claude-statusline.sh
   chmod +x ~/.claude/claude-statusline.sh
   ```

   Requires `jq` and `git` on your `PATH`.

2. Merge `statusline/settings-snippet.json` into `~/.claude/settings.json`
   (top-level keys `statusLine` and `hooks`). If you already have a `hooks`
   block, add the `UserPromptSubmit` / `Stop` entries to it instead of
   overwriting.

3. **Restart Claude Code** so the hooks register. Send a message → the mascot
   turns into 🤖🧠 (orange); when the reply finishes it relaxes to 😴💤 (blue).

## Customize

- **Different emoji:** edit the `anim_set=(🤖 🧠)` / `anim_set=(😴 💤)` arrays
  near the top of the mascot block in `claude-statusline.sh`.
- **Hide the `working`/`idle` label:** remove `${anim_label}` from the
  `mascot_segment=...` line.
- **Track length:** change `anim_w=6`.

## Uninstall

Remove the `statusLine` and the two `hooks` entries from
`~/.claude/settings.json`, then delete `~/.claude/claude-statusline.sh` and the
`~/.claude/.statusline-*` state files.
