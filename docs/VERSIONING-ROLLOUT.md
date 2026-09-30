# Portfolio Archive alignment — 2026-10-01

The following apps now have committed implementations of the agreed
`YYYY.MMDD.HHMM` UTC build identity. Product → Archive captures a fresh stamp
without version/build command arguments. Marketing versions remain separate in
`Config/Shared.xcconfig`, and shipping extensions share the app's identity.

These commits have been validated locally. They are not merged into main.
New branch publication and draft PR creation are pending approval; the existing
Orbari and central reference PRs also need their local updates pushed.

| App | Platforms verified | Local commit | Review status |
| --- | --- | --- | --- |
| OrgOrbari | ios, macos | `dc3312e9` | Local commit; publication pending approval |
| RelicPack | ios, macos | `cdd12b8c` | Local commit; publication pending approval |
| TrainieTalkie | ios | `a53ff1c9` | Local commit; publication pending approval |
| Restauranteer | ios | `ed58ee5a` | Local commit; publication pending approval |
| BananaBlitz | macos | `e3235713` | Local commit; publication pending approval |
| Lyrebird | macos | `4f9dc659` | Local commit; publication pending approval |
| FrameSplash | macos | `bb5b493e` | Local commit; publication pending approval |
| Icing | tvos | `3126cb3f` | Local commit; publication pending approval |
| PrivacyTracker | ios | `c42f5edf` | Local commit; publication pending approval |
| privacycommand | macos | `c014c57f` | Local commit; publication pending approval |
| Orbari | macos, ios | `646c1d58` | Update existing [PR #54](https://github.com/AdamXweb/Orbari/pull/54) |

## Verification

Fourteen real unsigned Release archives passed, covering all eleven apps and
both platforms for Orbari, OrgOrbari and RelicPack. The archive verifier confirms
Organizer/app marketing and build versions, timestamp parity, bundled extension
identity and release repository redaction. These are ordinary Xcode archive
builds with no supplied marketing/build numbers. Schemes and derived plist
processing generate the values before signing.

Shared regression checks cover failed/stale capture, UTC time, metadata preservation,
complete wrapper overrides, empty Fastlane inputs, signing command defaults and
extension mismatch detection. XcodeGen project generation, release syntax and
whitespace checks pass. Lyrebird's required swift build and swift test also pass
(371 tests). Existing signing choices are retained; privacycommand's embedded guest
staging now respects an explicitly unsigned Xcode build.

`just archive` uses the normal Xcode signing setup, regenerates projects where
required, and checks the produced archive. Each platform has a separate filename.
TrainieTalkie and RelicPack retain their prior export flows as `archive-export`.
No export, notarization, provisioning or upload was attempted. Signed distribution
still requires the app's Apple account, team and certificates. A legacy uploaded
integer build may require a marketing version bump before the first timestamp upload.

## Canonical reference

The shared implementation and integration instructions are in
[the central standard PR](https://github.com/AdamXweb/AdamXweb/pull/1).
The macOS menu bar/IAP work remains in
[Orbari PR #54](https://github.com/AdamXweb/Orbari/pull/54).
Live sandbox IAP and distribution signing were not validated by this Archive rollout.
