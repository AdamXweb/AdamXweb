# Shared build tracking code

Read the [portfolio standard](../../docs/VERSIONING.md) before integrating.
Copy the `Scripts` helpers and optionally `Sources/BuildInfo.swift` to equivalent
paths in the app, merge the xcconfig defaults, and wire every shipping target's
derived plist and shared scheme capture. Preserve the app's marketing version.

`prepare-build-info.py` makes Product → Archive generate a fresh stamp automatically,
before plist processing and signing. `build_identity.rb` captures one stamp for
Fastlane calls, including paired platform builds. `archive-app.py` reads the app's
`Config/ArchiveTargets.json`, regenerates an XcodeGen project when needed, archives,
and runs `verify-archive.py` against Organizer, app and extension metadata.
Use `--plan` to inspect the commands and `--unsigned` for compile/metadata validation.
Normal archives use the project's signing configuration and Apple account.

The generator and banner run with Bash 3.2+ on macOS or Linux and need Git,
`date`, `shasum`, and standard command-line tools. The Swift reader can be public
in a shared package used by iOS/macOS clients.

Run the reference regression suite from the repository root:

```bash
python3 standards/versioning/tests/test_buildinfo.py
python3 standards/versioning/tests/test_xcode_identity.py
ruby standards/versioning/tests/test_fastlane_identity.rb
python3 standards/versioning/tests/test_archive_command.py
```

`buildinfo.sh` detects the CI channel automatically unless explicitly overridden,
recognizes numeric marketing-version tags at HEAD, and preserves dirty/tagged as
independent flags. GitHub diagnostics identify the source before release fields
are redacted. `prepare-build-info.py` logs each target's actual UTC stamp and flags.
The regression suite includes missing/fetched tags, detached HEAD and CI overrides.
For app command coverage and release gates, see [BUILD-COMMANDS.md](../../docs/BUILD-COMMANDS.md).
