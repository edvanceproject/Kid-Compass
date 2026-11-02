#!/usr/bin/env bash
# kid-compass installer (macOS / Linux / WSL / Git Bash)
#
# Copies the kid-compass skill into the folders AI agents load skills from:
#   ~/.claude/skills/kid-compass   → Claude Code (Cursor reads it too)
#   ~/.agents/skills/kid-compass   → Codex, Cursor, GitHub Copilot, Gemini CLI and other agents
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/edvanceproject/Kid-Compass/main/install.sh | bash
#   curl -fsSL https://raw.githubusercontent.com/edvanceproject/Kid-Compass/main/install.sh | bash -s -- --agent codex
#   ./install.sh --project            # install into the current project instead of your home folder
#   ./install.sh --uninstall          # remove it again
set -euo pipefail

REPO="${KID_COMPASS_REPO:-edvanceproject/Kid-Compass}"
REF="${KID_COMPASS_REF:-main}"
SKILL="kid-compass"
SCOPE="global"
AGENTS="all"
ACTION="install"

usage() {
  cat <<EOF
kid-compass installer

Options:
  --agent LIST   which agents to install for, comma-separated (default: all)
                   claude   Claude Code                      (~/.claude/skills)
                   codex    OpenAI Codex                     (~/.agents/skills)
                   cursor   Cursor                           (~/.agents/skills)
                   copilot  GitHub Copilot                   (~/.agents/skills)
                   gemini   Gemini CLI                       (~/.agents/skills)
                   agents   any agent that reads .agents/skills
                   all      all of the above (two folders)
  --project      install into ./.claude/skills and ./.agents/skills of the current folder
  --global       install into your home folder (default)
  --ref REF      branch or tag to install (default: main)
  --uninstall    remove kid-compass from the chosen folders
  -h, --help     show this help
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --agent|--agents) AGENTS="${2:?--agent needs a value}"; shift 2 ;;
    --project) SCOPE="project"; shift ;;
    --global) SCOPE="global"; shift ;;
    --ref) REF="${2:?--ref needs a value}"; shift 2 ;;
    --uninstall) ACTION="uninstall"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [ "$SCOPE" = "global" ]; then BASE="$HOME"; else BASE="$(pwd)"; fi

# Work out which skills folders to use.
want_claude=0; want_agents=0
IFS=',' read -r -a list <<< "$AGENTS"
for a in "${list[@]}"; do
  case "$(echo "$a" | tr '[:upper:]' '[:lower:]' | xargs)" in
    all) want_claude=1; want_agents=1 ;;
    claude|claude-code) want_claude=1 ;;
    codex|cursor|copilot|github-copilot|gemini|gemini-cli|agents|universal) want_agents=1 ;;
    *) echo "Unknown agent: $a (try: claude, codex, cursor, copilot, gemini, all)" >&2; exit 1 ;;
  esac
done
targets=()
[ $want_claude -eq 1 ] && targets+=("$BASE/.claude/skills")
[ $want_agents -eq 1 ] && targets+=("$BASE/.agents/skills")

is_ours() { [ -f "$1/SKILL.md" ] && grep -q "^name: $SKILL\$" "$1/SKILL.md"; }

if [ "$ACTION" = "uninstall" ]; then
  for t in "${targets[@]}"; do
    if is_ours "$t/$SKILL"; then rm -rf "${t:?}/$SKILL"; echo "✓ removed $t/$SKILL"; else echo "· nothing to remove in $t"; fi
  done
  exit 0
fi

# Find the skill: a local clone next to this script, or download it from GitHub.
SRC=""
script_dir=""
if [ -n "${BASH_SOURCE[0]:-}" ] && [ -f "${BASH_SOURCE[0]}" ]; then
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi
if [ -n "$script_dir" ] && [ -f "$script_dir/skills/$SKILL/SKILL.md" ]; then
  SRC="$script_dir/skills/$SKILL"
else
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' EXIT
  url="https://codeload.github.com/$REPO/tar.gz/$REF"
  echo "Downloading $REPO ($REF)…"
  if command -v curl >/dev/null 2>&1; then curl -fsSL "$url" -o "$tmp/src.tar.gz"
  elif command -v wget >/dev/null 2>&1; then wget -qO "$tmp/src.tar.gz" "$url"
  else echo "Need curl or wget to download kid-compass." >&2; exit 1; fi
  tar -xzf "$tmp/src.tar.gz" -C "$tmp"
  SRC="$(find "$tmp" -type f -path "*/skills/$SKILL/SKILL.md" | head -n 1 | xargs dirname)"
  [ -n "$SRC" ] || { echo "Couldn't find skills/$SKILL in the download." >&2; exit 1; }
fi

for t in "${targets[@]}"; do
  mkdir -p "$t"
  if [ -e "$t/$SKILL" ]; then
    if is_ours "$t/$SKILL"; then rm -rf "${t:?}/$SKILL"
    else echo "! $t/$SKILL exists and isn't kid-compass — skipped" >&2; continue; fi
  fi
  cp -R "$SRC" "$t/$SKILL"
  find "$t/$SKILL" -name "__pycache__" -type d -prune -exec rm -rf {} + 2>/dev/null || true
  echo "✓ installed to $t/$SKILL"
done

echo
if command -v python3 >/dev/null 2>&1 && python3 -c "import yaml" >/dev/null 2>&1; then
  echo "Helper scripts ready (Python + PyYAML found)."
else
  echo "Optional: the helper scripts need Python 3 and PyYAML →  python3 -m pip install pyyaml"
  echo "          (the skill still works without them; the agent reads the registry directly)"
fi
echo
echo "Restart your agent, then ask something like:"
echo "  \"My daughter is 10, Class 5, in Pune and loves drawing — what can she take part in this year?\""
