#!/usr/bin/env bash
# Emits xcodebuild build-setting arguments describing the tree being built.
#
#   xcodebuild ... $(Scripts/buildinfo.sh)
#
# BUILD_CHANNEL  local (default) | ci | testflight | release
# BUILD_PROVENANCE  full (default) | minimal — `minimal` omits SHA and branch,
#                   set automatically for the `release` channel so a public
#                   binary carries nothing about a private repo.
set -euo pipefail

channel="${BUILD_CHANNEL:-local}"
provenance="${BUILD_PROVENANCE:-$([ "$channel" = release ] && echo minimal || echo full)}"

# Absent or unreadable repository (source export, artefact-only CI job) must
# degrade to empty provenance, never abort the build. `set -e` plus `pipefail`
# will kill an assignment whose pipeline fails, so every git call is guarded.
sha=""; branch=""; describe=""; diffid=""; tagged=NO; n=0

if git rev-parse --git-dir >/dev/null 2>&1 && git rev-parse HEAD >/dev/null 2>&1; then
  sha=$(git rev-parse --short=8 HEAD)
  branch=$(git rev-parse --abbrev-ref HEAD)
  n=$(git status --porcelain | wc -l | tr -d ' ')
  describe=$(git describe --tags --always --dirty 2>/dev/null || echo "")
  if git describe --tags --exact-match --match 'v[0-9]*' HEAD >/dev/null 2>&1; then tagged=YES; fi
  # Hash tracked changes AND untracked content — `git diff HEAD` alone ignores
  # untracked files, so a tree dirty only with new files would otherwise get
  # the constant SHA-256 of empty input (e3b0c442) on every build.
  if [ "$n" -gt 0 ]; then
    diffid=$( { git diff HEAD; git status --porcelain;
                git ls-files --others --exclude-standard -z \
                  | xargs -0 shasum -a 256 2>/dev/null || true;
              } | shasum -a 256 | cut -c1-8 )
  fi
fi

# `release` builds ship no repository detail. Keys stay present but empty so
# the plist shape is identical across channels; BuildInfo.swift treats an empty
# value as absent.
if [ "$provenance" = minimal ]; then sha=""; branch=""; describe=""; diffid=""; fi

# Capture the clock once: the number and timestamp must describe the same
# instant even when this invocation straddles a UTC minute/day boundary.
stamp=$(date -u '+%Y.%m%d.%H%M|%Y-%m-%dT%H:%M:%SZ')
cat <<EOF
BUILD_NUMBER=${stamp%%|*}
BUILD_SHA=$sha
BUILD_BRANCH=$branch
BUILD_DIRTY=$([ "$n" -gt 0 ] && echo YES || echo NO)
BUILD_DIRTY_FILES=$n
BUILD_DIFF_ID=$diffid
BUILD_DESCRIBE=$describe
BUILD_TAGGED=$tagged
BUILD_TIMESTAMP=${stamp#*|}
BUILD_CHANNEL=$channel
EOF
