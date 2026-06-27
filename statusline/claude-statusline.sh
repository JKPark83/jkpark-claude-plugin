#!/usr/bin/env bash
# Claude Code statusLine — inspired by Powerlevel10k classic layout
# Segments: dir | git branch+status [worktree] | model | effort | context%

input=$(cat)

# --- Data extraction ---
cwd=$(echo "$input" | jq -r '.cwd // .workspace.current_dir // empty')
model=$(echo "$input" | jq -r '.model.display_name // empty')
used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
git_worktree=$(echo "$input" | jq -r '.workspace.git_worktree // empty')
repo_owner=$(echo "$input" | jq -r '.workspace.repo.owner // empty')
repo_name=$(echo "$input" | jq -r '.workspace.repo.name // empty')
effort=$(echo "$input" | jq -r '.effort.level // .effort // empty')

# --- ANSI colors (dim-friendly) ---
RESET='\033[0m'
BOLD='\033[1m'
CYAN='\033[36m'
YELLOW='\033[33m'
GREEN='\033[32m'
RED='\033[31m'
BLUE='\033[34m'
DIM='\033[2m'
ORANGE='\033[38;5;208m'

# --- Directory segment ---
# Shorten home prefix to ~
short_dir="${cwd/#$HOME/~}"
dir_segment="${CYAN}${BOLD}${short_dir}${RESET}"

# --- Git segment ---
git_segment=""
if [ -n "$cwd" ] && git -C "$cwd" rev-parse --git-dir > /dev/null 2>&1; then
  branch=$(git -C "$cwd" --no-optional-locks symbolic-ref --short HEAD 2>/dev/null \
           || git -C "$cwd" --no-optional-locks rev-parse --short HEAD 2>/dev/null)
  if [ -n "$branch" ]; then
    # Check for uncommitted changes
    dirty=$(git -C "$cwd" --no-optional-locks status --porcelain 2>/dev/null | head -1)
    if [ -n "$dirty" ]; then
      git_color="${YELLOW}"
      git_icon="*"
    else
      git_color="${GREEN}"
      git_icon=""
    fi
    # Show worktree name if in a linked worktree
    if [ -n "$git_worktree" ]; then
      branch_display="${branch} [${git_worktree}]"
    else
      branch_display="${branch}"
    fi
    git_segment=" ${DIM}on${RESET} ${git_color} ${branch_display}${git_icon}${RESET}"
  fi
fi

# --- Repo segment (GitHub owner/name) ---
repo_segment=""
if [ -n "$repo_owner" ] && [ -n "$repo_name" ]; then
  repo_segment=" ${DIM}(${repo_owner}/${repo_name})${RESET}"
fi

# --- Model segment ---
model_segment=""
if [ -n "$model" ]; then
  model_segment=" ${DIM}|${RESET} ${BLUE}${model}${RESET}"
fi

# --- Context segment (progress bar) ---
ctx_segment=""
if [ -n "$used_pct" ]; then
  used_int=$(printf '%.0f' "$used_pct")
  if [ "$used_int" -ge 80 ]; then
    ctx_color="${RED}"
  elif [ "$used_int" -ge 50 ]; then
    ctx_color="${YELLOW}"
  else
    ctx_color="${GREEN}"
  fi
  # Build a 10-cell bar; round filled cells to nearest 10%
  bar_total=10
  filled=$(( (used_int + 5) / 10 ))
  [ "$filled" -gt "$bar_total" ] && filled=$bar_total
  [ "$filled" -lt 0 ] && filled=0
  bar=""
  i=0
  while [ "$i" -lt "$bar_total" ]; do
    if [ "$i" -lt "$filled" ]; then
      bar="${bar}█"
    else
      bar="${bar}░"
    fi
    i=$((i + 1))
  done
  ctx_segment=" ${DIM}|${RESET} ${DIM}ctx${RESET} ${ctx_color}${bar}${RESET} ${ctx_color}${used_int}%${RESET}"
fi

# --- Effort segment (per-mode icon) ---
effort_segment=""
if [ -n "$effort" ]; then
  case "$effort" in
    low)             effort_icon="🌱"; effort_color="${GREEN}"  ;;
    medium|mid|med)  effort_icon="⚡"; effort_color="${BLUE}"   ;;
    high)            effort_icon="🔥"; effort_color="${YELLOW}" ;;
    xhigh|max)       effort_icon="🚀"; effort_color="${RED}"    ;;
    *)               effort_icon="•";  effort_color="${DIM}"    ;;
  esac
  effort_segment=" ${DIM}|${RESET} ${effort_color}${effort_icon} ${effort}${RESET}"
fi

# --- Animated Claude mascot (state-aware emoji: working vs idle) ---
anim_state="$HOME/.claude/.statusline-anim-frame"
frame=$(cat "$anim_state" 2>/dev/null || echo 0)
echo $(( (frame + 1) % 100000 )) > "$anim_state"

# Mode is set by hooks: UserPromptSubmit -> working, Stop -> idle
mode=$(cat "$HOME/.claude/.statusline-mode" 2>/dev/null || echo idle)
if [ "$mode" = "working" ]; then
  anim_set=(🤖 🧠)            # Claude actively computing
  anim_color="${ORANGE}"
  anim_label="working"
else
  anim_set=(😴 💤)            # idle, waiting for you
  anim_color="${BLUE}"
  anim_label="idle"
fi
anim_e=${anim_set[$(( frame % ${#anim_set[@]} ))]}

anim_w=6                                    # track width (emoji are wide)
anim_period=$(( 2 * (anim_w - 1) ))         # ping-pong period
anim_pos=$(( frame % anim_period ))
[ "$anim_pos" -ge "$anim_w" ] && anim_pos=$(( anim_period - anim_pos ))

anim_track=""
ai=0
while [ "$ai" -lt "$anim_w" ]; do
  if [ "$ai" -eq "$anim_pos" ]; then
    anim_track="${anim_track}${anim_e}"
  else
    anim_track="${anim_track}${DIM}·${RESET}"
  fi
  ai=$((ai + 1))
done
mascot_segment="${anim_color}${anim_track}${RESET} ${DIM}${anim_label}${RESET} ${DIM}|${RESET} "

# --- Assemble ---
echo -e "${mascot_segment}${dir_segment}${git_segment}${repo_segment}${model_segment}${effort_segment}${ctx_segment}"
