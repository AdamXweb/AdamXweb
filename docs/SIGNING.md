# Portfolio Apple signing team

Adam Kostarelas (`6S9Q286XS9`) is the agreed Apple Developer signing team for
Xcode app projects across AdamXweb, adamXbot and privacykey. Use this team for
new projects and when repairing or regenerating existing projects.

## Project settings

Set `DEVELOPMENT_TEAM` to `6S9Q286XS9` for every build configuration. A project
default should cover app, extension, helper and test targets; remove blank or
different target overrides. Keep any existing Xcode `DevelopmentTeam` target
attributes consistent with the resolved build setting.

For generated projects, save the default in `project.yml` and any signing
`.xcconfig` used by the targets. Editing only the generated `.xcodeproj` loses
the setting at the next regeneration. An optional `Signing.local.xcconfig`
override is for a developer intentionally using another signing account.

Team selection is separate from signing style, certificates, provisioning,
bundle identifiers, marketing versions and repository ownership. Existing
unsigned CI and local ad hoc signing settings can remain in place. Continue
using the [portfolio versioning agreement](VERSIONING.md) for build numbers
and provenance.

## Local audit on 1 October 2026

Nineteen app projects were checked across the primary development checkouts,
older local app copies and Orbari's active app checkout. Seventeen projects
needed a team setting or a project default; TrainieTalkie and privacycommand
already resolved to the agreed team. Orbari's app and share extension were
already correct, and its purchase test host now inherits the project default.

All 99 target and configuration combinations passed the project setting
audit. All 39 native Xcode configuration queries resolved the correct team
for every target, including TrainieTalkie's Debug Premium configuration.
Fourteen XcodeGen specifications regenerated successfully with the correct
team, including the local rotation probe. Dependency projects and duplicate
worktrees belonging to other tasks were excluded.

App checkout changes are local and uncommitted. This audit confirms team
configuration; signed archives, provisioning and uploads were not performed.
