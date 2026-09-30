# Shared build tracking code

Read the [portfolio standard](../../docs/VERSIONING.md) before integrating.
Copy `Scripts/buildinfo.sh`, `Scripts/banner.sh` and `Sources/BuildInfo.swift`
to equivalent paths in the app, merge the xcconfig defaults, and wire every
shipping target's plist. Preserve the app's existing marketing version.

The generator and banner run with Bash 3.2+ on macOS or Linux and need Git,
`date`, `shasum`, and standard command-line tools. The Swift reader can be public
in a shared package used by iOS/macOS clients.

Run the reference regression suite from the repository root:

```bash
python3 standards/versioning/tests/test_buildinfo.py
```
