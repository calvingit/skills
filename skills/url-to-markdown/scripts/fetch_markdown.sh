#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: fetch_markdown.sh <url> [output_path]

Fetch a public webpage as markdown using fallback services.
The script tries:
1. https://markdown.new
2. https://r.jina.ai
3. https://defuddle.md
EOF
}

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  usage >&2
  exit 1
fi

input_url="$1"
output_path="${2:-}"

if [ -z "$output_path" ]; then
  sanitized_name="$(
    printf '%s' "$input_url" \
      | sed -E 's#^[a-zA-Z]+://##' \
      | sed -E 's#[/?#&=:%]+#-#g' \
      | sed -E 's#-+#-#g; s#^-##; s#-$##'
  )"
  [ -n "$sanitized_name" ] || sanitized_name="page"
  output_path="${sanitized_name}.md"
fi

services=(
  "https://markdown.new"
  "https://r.jina.ai"
  "https://defuddle.md"
)

temp_file="$(mktemp)"
error_file="$(mktemp)"
errors=()
success_service=""

cleanup() {
  rm -f "$temp_file"
  rm -f "$error_file"
}

trap cleanup EXIT

for service in "${services[@]}"; do
  request_url="${service}/${input_url}"

  mkdir -p "$(dirname "$output_path")"

  if curl \
    --fail \
    --silent \
    --show-error \
    --location \
    --connect-timeout 10 \
    --max-time 10 \
    --output "$temp_file" \
    "$request_url" \
    2>"$error_file"; then
    if [ -s "$temp_file" ]; then
      mv "$temp_file" "$output_path"
      success_service="$service"
      printf 'Saved markdown to %s\n' "$output_path"
      printf 'Source service: %s\n' "$success_service"
      exit 0
    fi

    errors+=("${service}: empty response")
    : > "$temp_file"
    : > "$error_file"
    continue
  fi

  curl_error="$(tr '\n' ' ' <"$error_file" | sed -E 's/[[:space:]]+/ /g; s/^ //; s/ $//')"
  [ -n "$curl_error" ] || curl_error="curl request failed"
  errors+=("${service}: ${curl_error}")
  : > "$temp_file"
  : > "$error_file"
done

printf 'Failed to fetch markdown for %s\n' "$input_url" >&2
for error in "${errors[@]}"; do
  printf '%s\n' "$error" >&2
done
exit 1
