#!/usr/bin/env bash
set -euo pipefail

# ---------- helpers ----------
err()  { echo "Error: $*" >&2; }
warn() { echo "Warning: $*" >&2; }

# Expand ~ and resolve a reasonable absolute path (without requiring the file to exist yet).
resolve_path() {
  local p="$1"

  # Strip surrounding quotes (common when pasting paths)
  p="${p%\"}"; p="${p#\"}"
  p="${p%\'}"; p="${p#\'}"

  # Expand leading ~
  if [[ "$p" == "~" || "$p" == "~/"* ]]; then
    p="${HOME}${p:1}"
  fi

  # If it's already absolute, keep it; otherwise prefix with current working directory
  if [[ "$p" != /* ]]; then
    p="$(pwd)/$p"
  fi

  # Canonicalize directory portion if possible (works even if file doesn't exist yet)
  local d
  d="$(dirname "$p")"
  if [[ -d "$d" ]]; then
    local absd
    absd="$(cd "$d" && pwd -P)"
    p="$absd/$(basename "$p")"
  fi

  echo "$p"
}

# ---------- locate input notebook ----------
while :; do
  read -r -p "Enter the path to the .ipynb file (absolute or relative): " in_raw
  in="$(resolve_path "${in_raw:-}")"

  if [[ -z "${in_raw:-}" ]]; then
    err "No input provided."
    continue
  fi

  if [[ "${in}" != *.ipynb ]]; then
    err "Input must end with .ipynb (got: $(basename "$in"))."
    continue
  fi

  if [[ ! -e "${in}" ]]; then
    err "File not found: $in"
    warn "Tip: drag-and-drop the file into Terminal, or paste the full path."
    continue
  fi

  if [[ ! -f "${in}" ]]; then
    err "Path exists but is not a regular file: $in"
    continue
  fi

  if [[ ! -r "${in}" ]]; then
    err "File is not readable (permissions issue): $in"
    continue
  fi

  break
done

# ---------- output directory (default: ./outputs) ----------
default_out="./.outputs"
read -r -p "Enter output directory (press Enter for '${default_out}'): " out_raw
out_raw="${out_raw:-$default_out}"

out_dir="$(resolve_path "$out_raw")"

# If they accidentally gave a file path, treat it as an error
if [[ -e "$out_dir" && ! -d "$out_dir" ]]; then
  err "Output path exists but is not a directory: $out_dir"
  exit 1
fi

# Create directory if needed
if [[ ! -d "$out_dir" ]]; then
  if ! mkdir -p "$out_dir" 2>/dev/null; then
    err "Failed to create output directory: $out_dir"
    warn "Check permissions or choose a different location."
    exit 1
  fi
fi

# Ensure writable
if [[ ! -w "$out_dir" ]]; then
  err "Output directory is not writable: $out_dir"
  warn "Check permissions or choose a different directory."
  exit 1
fi

# ---------- conversion with robust error capture ----------
log_file="$out_dir/nbconvert_$(date +%Y%m%d_%H%M%S).log"

if ! command -v jupyter >/dev/null 2>&1; then
  err "'jupyter' command not found on PATH."
  warn "If you installed with pip --user, ensure your user bin directory is on PATH."
  exit 127
fi

echo "Converting:"
echo "  Input : $in"
echo "  Output: $out_dir"
echo "Log:"
echo "  $log_file"
echo

# Capture stdout+stderr to a log, while still showing it in the terminal
if ! jupyter nbconvert --to markdown --output-dir "$out_dir" "$in" 2>&1 | tee "$log_file"; then
  err "nbconvert failed. See log: $log_file"
  exit 1
fi

echo
echo "Done. Markdown written to: $out_dir"