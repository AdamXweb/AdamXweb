# Portfolio Archive alignment — 2026-10-01

The following apps now have committed implementations of the agreed
`YYYY.MMDD.HHMM` UTC build identity. Product → Archive captures a fresh stamp
without version/build command arguments. Marketing versions remain separate in
`Config/Shared.xcconfig`, and shipping extensions share the app's identity.

All eleven app branches are published and their PRs are merged into main on
2026-10-01. The central standard PR is published, ready for review, and remains
open because the active account has no write/merge permission in AdamXweb/AdamXweb.
It is submitted from the adamXbot/AdamXweb fork.

| App | Platforms verified | Pull request | Status |
| --- | --- | --- | --- |
| OrgOrbari | ios, macos | [PR #15](https://github.com/adamXbot/orgorbari/pull/15) | Merged |
| RelicPack | ios, macos | [PR #78](https://github.com/adamXbot/voyari/pull/78) | Merged |
| TrainieTalkie | ios | [PR #192](https://github.com/AdamXweb/TrainieTalkie/pull/192) | Merged |
| Restauranteer | ios | [PR #27](https://github.com/adamXbot/restauranteer-ios/pull/27) | Merged |
| BananaBlitz | macos | [PR #11](https://github.com/adamXbot/BananaBlitz/pull/11) | Merged |
| Lyrebird | macos | [PR #13](https://github.com/adamXbot/lyrebird/pull/13) | Merged |
| FrameSplash | macos | [PR #8](https://github.com/adamXbot/FrameSplash/pull/8) | Merged |
| Icing | tvos | [PR #8](https://github.com/adamXbot/Icing/pull/8) | Merged |
| PrivacyTracker | ios | [PR #2](https://github.com/privacykey/privacytracker-ios/pull/2) | Merged |
| privacycommand | macos | [PR #21](https://github.com/privacykey/privacycommand/pull/21) | Merged |
| Orbari | macos, ios | [PR #54](https://github.com/AdamXweb/Orbari/pull/54) | Merged |

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

## CI notes

The identity regression checks pass across the app PRs. Some optional fleet jobs
were queued at merge; no required checks were overridden. TrainieTalkie's Debug
and UI smoke jobs fail before compilation while provisioning an incompatible
iPhone 17 Pro / iOS 27.1 simulator. This same error occurs on its unchanged main
revision from 2026-09-25. Its actual unsigned archive and identity checks pass;
the simulator runner issue remains. Orbari's old Xcode 26-only CI selector was
updated to accept supported newer Xcodes and verified locally with Xcode 27.1.
Its six StoreKit tests passed again after the final changes.

## Canonical reference

The shared implementation and integration instructions are in
[the central standard PR](https://github.com/AdamXweb/AdamXweb/pull/1).
The macOS menu bar/IAP work remains in
[Orbari PR #54](https://github.com/AdamXweb/Orbari/pull/54).
Live sandbox IAP and distribution signing were not validated by this Archive rollout.
