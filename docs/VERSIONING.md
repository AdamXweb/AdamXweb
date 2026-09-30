# Portfolio versioning and build tracking

Adopted 2026-09-09 in the Claude conversation **iOS build tracking and versioning**;
reconfirmed 2026-09-30. This is the shared standard for the app portfolio across
`AdamXweb/*`, `adamXbot/*` and `privacykey/*`. Apply it when working on an app in
scope; adoption remains a per-repository change.

## Version and build number

| Field | Rule | Example |
| --- | --- | --- |
| Marketing version | Hand-chosen `MAJOR.MINOR.PATCH`, integers only | `1.0.1` |
| Build number | Generated `YYYY.MMDD.HHMM`, **UTC** | `2026.0930.0815` |
| Provenance | Separate metadata for commit, branch, dirty state and channel | `BuildSHA`, `BuildBranch` |

Never replace the build format with minutes since an epoch, a commit count,
or a CI run number. Never commit a generated build number or reset the clock
sequence on a version bump. One minute has one build number: wait until the next
UTC minute before making another distinct upload to the same version train.

Each Apple app declares its marketing version once, in `Config/Shared.xcconfig`.
Use `CURRENT_PROJECT_VERSION = $(BUILD_NUMBER)` for every shipping target.
Remove literal overrides from `project.yml` and the generated project. An app,
widget, share extension and other bundled extensions must share both values.
An xcconfig fallback of `BUILD_NUMBER = 0` is a sentinel, never a shippable number.

Use `0.x.y` before public release, then `1.0.0` at launch. A patch is a fix, a
minor version adds visible functionality, and a major version changes the user's
workflow or data. Make a version bump in a dedicated `release: x.y.z` commit
with the changelog and an annotated `vX.Y.Z` tag. Keep prerelease labels in the
channel rather than in the marketing version.

## Shared implementation

The tested reference files are in [`standards/versioning`](../standards/versioning/):

- `Scripts/buildinfo.sh`: emits build settings from one UTC clock capture.
- `Scripts/banner.sh`: prints the version and provenance before building.
- `Sources/BuildInfo.swift`: reads the stamped plist for Settings → About.
- `Config/Shared.xcconfig`: defaults to merge with the app's own configuration.

Copy the reference files into an app's repository and commit them there. Builds
must work from their own checkout; fetching a changing script during a release
would make that release harder to reproduce. Keep the copied generator and banner
identical to the reference, with app integration in separate files.

Generate the stamp outside a sandboxed Xcode build phase. From the repository
root, capture it once and pass the same arguments to every artifact:

```bash
info="$(Scripts/buildinfo.sh)"
BUILD_INFO="$info" Scripts/banner.sh MyApp
settings=()
while IFS= read -r setting; do settings+=("$setting"); done <<< "$info"
xcodebuild ... -destination 'generic/platform=iOS Simulator' "${settings[@]}" build
xcodebuild ... -destination 'generic/platform=macOS' "${settings[@]}" build
```

`BUILD_CHANNEL` is `local`, `ci`, `testflight`, or `release`. Capture once in
Fastlane and CI as well. The number and timestamp must come from the same instant.
Separate platform invocations must receive that same complete stamp, even if the
build crosses a minute boundary.

Map these plist keys on **every shipping target**, together with
`CFBundleShortVersionString: $(MARKETING_VERSION)` and
`CFBundleVersion: $(CURRENT_PROJECT_VERSION)`:

| Plist key | Setting |
| --- | --- |
| `BuildSHA` | `BUILD_SHA` |
| `BuildBranch` | `BUILD_BRANCH` |
| `BuildDirty` | `BUILD_DIRTY` |
| `BuildDirtyFiles` | `BUILD_DIRTY_FILES` |
| `BuildDiffID` | `BUILD_DIFF_ID` |
| `BuildDescribe` | `BUILD_DESCRIBE` |
| `BuildTagged` | `BUILD_TAGGED` |
| `BuildTimestamp` | `BUILD_TIMESTAMP` |
| `BuildChannel` | `BUILD_CHANNEL` |

With XcodeGen, declare both bundle version fields explicitly in each target's
`info.properties`; otherwise generated defaults can silently win. **Inspect the
finished app and extension plists**, rather than relying on resolved settings.
Missing repositories must produce empty provenance without failing the build.

Orbari's shared schemes capture a fresh stamp in a build pre-action, then
`Scripts/prepare-build-info.py` writes derived source plists that Xcode processes
and signs normally. This makes ⌘R and Archive accurate too. Other apps must wire
an equivalent capture or use their build wrapper; never display stale provenance.

## Release pipeline integration

The existing `privacykey/gh-workflows` iOS pipeline's `build_number: auto` uses
minutes since an epoch. For a Fastlane consumer of this standard, set:

```yaml
build_number: project
use_fastlane: true
```

The shared pipeline then exports `BUILD_NUMBER=""`. The lane must interpret empty
or missing input as **generate a fresh stamp**, using `Scripts/buildinfo.sh`.
A nonempty explicit override is optional. Do not retain the old epoch constant
in a second generator. Export with `manageAppVersionAndBuildNumber: false` so
Apple's export step preserves the chosen identity.

Release paths check that the pushed tag matches the marketing version before
loading signing material, reject dirty archives unless explicitly overridden,
and reject uploads from an untagged commit unless explicitly forced. Warn when
archiving away from `main`. Local builds remain easy to run on dirty branches.

`BUILD_CHANNEL=release` defaults to minimal provenance: SHA, branch, describe
and diff ID are empty, so public binaries carry no private repository details.
A clean, tagged release displays the marketing version alone. Other builds show
version, build number, commit/branch and an amber warning for uncommitted changes.
Settings → About should let the user copy the complete build report.

## Migrating an existing version train

Check App Store Connect's highest uploaded build before the first upload under
this format. Comparison is component-wise: `2026.0930.0815` sorts below `84438`
because `2026 < 84438`. If an old integer build has been uploaded, move to the
timestamp format with a marketing version bump to start a fresh version train.
Do not silently keep an epoch scheme merely because an older workflow uses it.

## Release records and other stacks

Each app owns its current version, annotated tags and changelog. GitHub Releases
record the artifact, build number and SHA; App Store Connect or the Sparkle
appcast records what shipped. A portfolio view should derive from those records,
rather than introducing a hand-maintained versions spreadsheet.

Node apps keep the chosen version in `package.json`, Rust in `Cargo.toml`, and
SwiftPM tools in a version constant. Generate equivalent `buildinfo.json` or
compiled provenance and expose it through About, `--version`, or `/api/version`.
For separately versioned products in one repository, reserve `vX.Y.Z` for the
primary product and use `<artifact>-vX.Y.Z` for the others.

The rollout decisions excluded Mantis, PickPedia and MacWallpaper; bundlefacts,
cookiemonster and MacOSauditor were deferred. Lyrebird is in scope. This document
does not change those scope decisions or claim all repositories have adopted it.

## Verification

Run `python3 standards/versioning/tests/test_buildinfo.py` in this repository.
The regression checks cover UTC/year-boundary identity, clean/tagged and dirty
repositories, untracked content, missing repositories and release redaction.
For an app integration, also build each platform, inspect the built plists, and
confirm all artifacts carry the same version, build number and timestamp.
