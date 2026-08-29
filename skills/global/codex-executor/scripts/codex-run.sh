#!/usr/bin/env bash

set -euo pipefail

MODE="${1:-analysis}"
shift || true

JSON=false
SESSION=""
TIMEOUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json)
      JSON=true
      shift
      ;;
    --session)
      SESSION="$2"
      shift 2
      ;;
    --timeout)
      TIMEOUT="$2"
      shift 2
      ;;
    *)
      break
      ;;
  esac
done

run_codex() {
  local args=("$@")

  if [[ "$JSON" == true ]]; then
    args+=(--json)
  fi

  if [[ -n "$TIMEOUT" ]]; then
    timeout "$TIMEOUT" codex exec "${args[@]}"
  else
    codex exec "${args[@]}"
  fi
}

case "$MODE" in
  analysis)
    run_codex --sandbox read-only "$@"
    ;;

  write)
    run_codex --sandbox workspace-write --full-auto "$@"
    ;;

  full)
    run_codex --sandbox danger-full-access --full-auto "$@"
    ;;

  resume)
    if [[ -n "$SESSION" ]]; then
      echo "$*" | codex exec resume "$SESSION"
    else
      echo "$*" | codex exec resume --last
    fi
    ;;

  *)
    echo "Usage: codex-run.sh {analysis|write|full|resume} [--json] [--session id] [--timeout seconds] <prompt>"
    exit 1
    ;;
esac
