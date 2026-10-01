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

## Publication of the provenance audit

All eleven app corrections are merged; the shared pipeline fix is merged separately.

- OrgOrbari: https://github.com/adamXbot/orgorbari/pull/16 (`69d6bfe4`).
- RelicPack: https://github.com/adamXbot/voyari/pull/79 (`77614e3e`).
- TrainieTalkie: https://github.com/AdamXweb/TrainieTalkie/pull/193 (`333c8532`).
- Restauranteer: https://github.com/adamXbot/restauranteer-ios/pull/28 (`267ff2fe`).
- BananaBlitz: https://github.com/adamXbot/BananaBlitz/pull/12 (`4c6a4e74`).
- Lyrebird: https://github.com/adamXbot/lyrebird/pull/14 (`7bad9fb8`).
- FrameSplash: https://github.com/adamXbot/FrameSplash/pull/9 (`23895dec`).
- Icing: https://github.com/adamXbot/Icing/pull/9 (`1c102fae`).
- PrivacyTracker: https://github.com/privacykey/privacytracker-ios/pull/3 (`f64d4eb9`).
- privacycommand: https://github.com/privacykey/privacycommand/pull/22 (`67ccdecd`).
- Orbari: https://github.com/AdamXweb/Orbari/pull/55 (`2db1bb1d`).
- Shared Apple pipelines: https://github.com/privacykey/gh-workflows/pull/17 (`57d245db`).

All app provenance CI checks pass. Some optional app/fleet checks were still queued or running at merge. TrainieTalkie UI smoke still fails before compilation in the unchanged iPhone 17 Pro/iOS 27.1 simulator provisioner (CoreSimulator 403, exit 147), matching unchanged main on 2026-09-25. No required checks were bypassed.

The central reference remains in https://github.com/AdamXweb/AdamXweb/pull/1, which needs the repository owner to merge.
