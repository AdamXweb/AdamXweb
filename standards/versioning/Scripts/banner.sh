#!/usr/bin/env bash
# Human-readable rendering of Scripts/buildinfo.sh, printed before a build so
# you know what you are about to test. Usage: Scripts/banner.sh [AppName]
set -euo pipefail
cd "$(dirname "$0")/.."

# Parse data instead of evaluating repository-controlled branch/tag names.
# A wrapper can supply the stamp it will also pass to xcodebuild.
info="${BUILD_INFO:-$(Scripts/buildinfo.sh)}"
while IFS='=' read -r key value; do
  case "$key" in
    BUILD_NUMBER|BUILD_SHA|BUILD_BRANCH|BUILD_DIRTY|BUILD_DIRTY_FILES|BUILD_DIFF_ID|BUILD_DESCRIBE|BUILD_TAGGED|BUILD_TIMESTAMP|BUILD_CHANNEL)
      printf -v "$key" '%s' "$value" ;;
  esac
done <<< "$info"

name="${1:-$(basename "$PWD")}"
# MARKETING_VERSION lives in Config/Shared.xcconfig (standard) or, in repos not
# yet migrated, project.yml. Only read files that exist: sed exits non-zero on a
# missing file, and under `set -e`/`pipefail` that would kill the banner
# silently on exactly the repos that have not adopted the xcconfig yet.
vfiles=""
for f in Config/Shared.xcconfig project.yml; do [ -f "$f" ] && vfiles="$vfiles $f"; done
version=""
if [ -n "$vfiles" ]; then
  # shellcheck disable=SC2086
  version=$(sed -nE 's/^[[:space:]]*MARKETING_VERSION[[:space:]]*[=:][[:space:]]*"?([0-9.]+)"?.*/\1/p' \
              $vfiles 2>/dev/null | head -1 || true)
fi
version="${version:-0.0.0}"

if [ -t 1 ]; then bold=$'\033[1m'; dim=$'\033[2m'; amber=$'\033[33m'; off=$'\033[0m'
else bold=""; dim=""; amber=""; off=""; fi

printf '%s▸ %s %s (%s)%s\n' "$bold" "$name" "$version" "$BUILD_NUMBER" "$off"
if [ -n "$BUILD_SHA" ]; then
  printf '  commit  %s   branch  %s\n' "$BUILD_SHA" "$BUILD_BRANCH"
else
  printf '  commit  %s(none recorded — no repository)%s\n' "$dim" "$off"
fi
if [ "$BUILD_DIRTY" = YES ]; then
  printf '  tree    %s⚠ DIRTY — %s files (diff %s)%s\n' "$amber" "$BUILD_DIRTY_FILES" "$BUILD_DIFF_ID" "$off"
  printf '          %sthis build matches no commit and cannot be reproduced%s\n' "$amber" "$off"
elif [ "$BUILD_TAGGED" = YES ]; then
  printf '  tree    clean · %s\n' "$BUILD_DESCRIBE"
else
  printf '  tree    clean · %s%s%s\n' "$dim" "${BUILD_DESCRIBE:-untagged}" "$off"
fi
