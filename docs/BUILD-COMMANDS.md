# Portfolio just commands and build provenance

Audit date: 2026-10-01. Eleven apps in the agreed rollout scope.

`just info` previews the source identity: UTC build stamp, commit, branch, dirty-file count, tag-at-HEAD and channel. It does not reserve the stamp for a later build. `just archive` captures a fresh stamp, creates an Archive and verifies Organizer/app/extension metadata; exporting or uploading is a separate command. Product → Archive does the capture automatically through the shared scheme.

Dirty means tracked modifications or non-ignored untracked files. Ignored build products are excluded. A version tag (`vX.Y` or `vX.Y.Z`) at HEAD and dirty files are independent flags: both can be YES. A clean tagged source alone does not prove signing, export or App Store publication. A release-channel Archive may be untagged or dirty.

GitHub app builds automatically use the `ci` channel; explicit local/testflight/release choices take precedence. Archive defaults to `release` and redacts SHA/branch/describe/diff from binaries, while retaining dirty/tagged/timestamp/channel fields. CI source diagnostics remain in logs. Shared pipelines also report the checkout SHA, branch/detached state, dirty/tag flags and trigger in the job summary. PR jobs may build GitHub's synthetic merge commit; HEAD is reported accurately rather than replaced with the source branch's SHA.

Tag detection requires fetched tag refs. App build workflows and the updated shared pipelines fetch full history and tags. Shared pipeline consumers use an exact commit pin for these corrections; the moving v1 tag is unchanged.

Identification is consistent; clean-tree release enforcement is not universal. Do not infer a universal clean/tagged publishing gate from the presence of metadata.

## OrgOrbari

Repository: https://github.com/adamXbot/orgorbari. Source audited: `a38bdf6fd944766add6995212638bef3321effcd`.

App CI builds macOS and iOS Simulator and runs the headless harness. Shared iOS Release validation runs on PR/main; signed IPA export requires manual dispatch with the signed-archive checkbox. No macOS distribution workflow. Website deployment is separate.

```text
Available recipes:
    default                # List available commands
    archive platform="ios" # Regenerate the project, Archive, and verify its app/extension build identity.

    [dev]
    build                  # tree (docs/VERSIONING.md §5).
    build-ios              # Build the iOS Simulator app using the existing local build directory
    build-mac              # Build the macOS app using the existing local build directory
    info                   # What commit is this working tree, and is it dirty? (docs/VERSIONING.md §5)
    test                   # Run the existing headless Swift test suites (requires full Xcode)
    lint                   # Run the app's localization guard

    [website]
    run port="4173"        # Serve the shared Next.js/vinext website locally
    changelog port="4173"  # Regenerate the static changelog and RSS after editing website/changelog.json
    llms port="4173"       # Refresh AI deployment references from the public guide and customer notices
    check                  # Check website links, AI exports, RSS, AppConfig and JavaScript offline
    site-build             # Prepare public files and production RSS links without publishing
    deploy-check           # Build and check the complete Cloudflare Worker locally
    db-local               # Apply D1 migrations locally after a local Worker preview creates its database
    icons                  # Export the current OrgOrbari Icon Composer artwork into local website assets

    [deploy]
    deploy                 # Publish the website to Cloudflare; requires an authenticated Cloudflare account
    db-migrate             # Apply D1 migrations to the remote database before a production deployment
```

## RelicPack

Repository: https://github.com/adamXbot/voyari. Source audited: `625d423edc31078617c912dadf617445f1c78cba`.

CI runs package tests, native app builds, UI/StoreKit tests and localization checks. No tag-triggered app release workflow; archive-export and beta are local entry points. beta validates signing/export, but does not require a clean tree or a version tag.

```text
Available recipes:
    default                                       # Show the available commands.
    archive platform="ios"                        # Archive with the normal Xcode signing setup and verify its shared identity.

    [dev]
    setup                                         # Fresh checkout: install tooling and generate the project
    gen                                           # names: git ignores them, so a pull never removes them, and Xcode reopens them.
    info                                          # What commit is this working tree, and is it dirty? (docs/VERSIONING.md §5)
    build                                         # Build iOS + macOS, unsigned (banner first)
    mac-run args=""                               # Launch the Mac app in an isolated store (--sample, --keep, --no-build)

    [test]
    test package=""                               # swift test over the SPM packages (name one to narrow)
    ui-test filter=""                             # iPhone UI journeys on a disposable simulator (pass a filter to narrow)
    purchase-test                                 # The Apple StoreKit purchase suite (separate test plan)
    localization                                  # Localization guard (the CI job, run locally)

    [release]
    release-plan platform="ios"                   # Print the archive/export plan without credentials or a build
    release-check                                 # Validate signing inputs without archiving
    archive-export platform="ios"                 # Signed Release archive + export, no upload (platform: ios|macos)
    beta platform="ios"                           # Archive and upload to TestFlight (platform: ios|macos)
    clean                                         # Remove build products and the generated project

    [worker]
    worker-install                                # Install the locked local Google Worker tooling
    worker-test                                   # Run Worker runtime/verification tests and TypeScript checks
    worker-dev                                    # Start the Google Worker locally; requires local .dev.vars secrets
    worker-dry-run                                # Bundle and validate the Worker without uploading or deploying
    worker-deploy environment="production"        # Deploy the Google Worker using the current Wrangler account
    worker-secret-google environment="production" # Interactively upload the Google Places API secret
    # Upload an Apple In-App Purchase .p8 key from a local file without printing it
    worker-secret-apple key_file environment="production"
    worker-logs environment="production"          # Stream Worker operational events; the Worker never logs queries or keys
    worker-configure-app url                      # Write the local app endpoint config from an HTTPS origin
```

## TrainieTalkie

Repository: https://github.com/AdamXweb/TrainieTalkie. Source audited: `562982b821b9ad712b1a507c4b6f7227b6f65767`.

CI includes unit/UI, icons, CodeQL and the stack probe. Shared iOS Release validation runs on PR/main; signed IPA export requires manual dispatch with the signed-archive checkbox and CloudKit preflight. Local upload through archive.sh rejects dirty files unless ALLOW_DIRTY=1; fastlane beta has no equivalent clean-tree gate. Existing fleet simulator failures are independent of provenance.

```text
Available recipes:
    default                               # Show the available commands.
    setup                                 # Fresh checkout: generate the Xcode project (and Ruby gems, if fastlane is used).
    gen                                   # Regenerate the Xcode project after editing project.yml or adding files.
    build                                 # build, so you always know what you are about to test (docs/VERSIONING.md §5).
    test                                  # Unit tests on a clean, dedicated simulator
    ui-test filter="TrainieTalkieUITests" # UI tests (slow; pass a filter to narrow)
    demo                                  # Build, install and launch on a simulator with a seeded demo state.
    schema-check                          # Is Production's CloudKit schema in step with Development?
    archive-export args=""                # Archive + export locally (schema pre-flight + dSYMs kept)
    upload                                # Archive and upload to TestFlight (App Store Connect API key required).
    beta                                  # TestFlight via the fastlane lane CI uses
    stack-probe                           # Dispatch the iOS 27 metadata-overflow probe
    clean                                 # Remove build products and the generated project.
    archive platform="ios"                # Archive using the shared scheme identity and verify the completed archive.
    info                                  # Show the UTC build preview, commit, dirty files, tag-at-HEAD and channel.
```

## Restauranteer

Repository: https://github.com/adamXbot/restauranteer-ios. Source audited: `d603b15e4bf086c19fb0638b8ba6464ffab206b2`.

CI runs packages and simulator app/tests. Shared iOS release runs on v* tags or manual dispatch and exports an IPA without uploading it. The pipeline captures tag-at-HEAD; it does not universally enforce tag/marketing-version equality or reject dirty builds.

```text
Available recipes:
    default                # App build commands.
    archive platform="ios" # Regenerate the project, Archive, and verify its app/extension build identity.
    info                   # Show the UTC build preview, commit, dirty files, tag-at-HEAD and channel.
```

## BananaBlitz

Repository: https://github.com/adamXbot/BananaBlitz. Source audited: `0a47a3c3ee421ea82cff577d024115c02aa127cc`.

CI runs unsigned macOS tests. A v* tag starts signing/notarization, DMG packaging, GitHub Release and appcast publishing. The workflow checks tag versus marketing version. release-local has no clean-tree or tag gate.

```text
Available recipes:
    default                  # List available commands
    archive platform="macos" # Regenerate the project, Archive, and verify its app/extension build identity.
    info                     # Show the UTC build preview, commit, dirty files, tag-at-HEAD and channel.

    [dev]
    setup                    # Generate BananaBlitz.xcodeproj from project.yml (requires xcodegen)
    test                     # Build and run the unit tests (unsigned Debug, same as CI)
    clean                    # Remove build and release outputs

    [ship]
    release version          # Tag v<version> and push it to trigger the release workflow
    release-local            # Build, sign, notarize and package the DMG locally (needs Developer ID + notary env)
```

## Lyrebird

Repository: https://github.com/adamXbot/lyrebird. Source audited: `d536bd51b0053af210ab6a6c28db2c224d0c3a59`.

Only build-identity fixture CI exists; no automated Apple app build/test or distribution workflow. Required local Swift package build/tests pass separately.

```text
Available recipes:
    default                  # App build commands.
    archive platform="macos" # Regenerate the project, Archive, and verify its app/extension build identity.
    info                     # Show the UTC build preview, commit, dirty files, tag-at-HEAD and channel.
```

## FrameSplash

Repository: https://github.com/adamXbot/FrameSplash. Source audited: `c80adc803818be2fb69ee20aebb027a936dbeeee`.

Shared macOS App CI builds/tests the app. Shared Sparkle release builds signed/notarized DMG, appcast and GitHub Release; optional Homebrew publication is separate. Tag pushes and manual release_tag use that exact tagged checkout and check marketing version. The local release.sh has no clean-tree or tag gate.

```text
Available recipes:
    default                  # App build commands.
    archive platform="macos" # Regenerate the project, Archive, and verify its app/extension build identity.
    info                     # Show the UTC build preview, commit, dirty files, tag-at-HEAD and channel.
```

## Icing

Repository: https://github.com/adamXbot/Icing. Source audited: `ba76a08aed4d8ba76eb20de202a2bcb9e8412e8b`.

Only build-identity fixture CI exists; no automated tvOS app build/test or distribution workflow.

```text
Available recipes:
    default                 # App build commands.
    archive platform="tvos" # Regenerate the project, Archive, and verify its app/extension build identity.
    info                    # Show the UTC build preview, commit, dirty files, tag-at-HEAD and channel.
```

## PrivacyTracker

Repository: https://github.com/privacykey/privacytracker-ios. Source audited: `57421f1fc80377e33e5ee0606b3bd3ad61da742b`.

CI runs package tests and an unsigned iOS Simulator build. No signed release/export workflow.

```text
Available recipes:
    default                # App build commands.
    archive platform="ios" # Regenerate the project, Archive, and verify its app/extension build identity.
    info                   # Show the UTC build preview, commit, dirty files, tag-at-HEAD and channel.
```

## privacycommand

Repository: https://github.com/privacykey/privacycommand. Source audited: `0fc43d4f125deffe3deb9385e1a56d2f86758e36`.

SPM CI tests the package/CLI; shared App CI builds/tests the macOS Xcode app. just build/test cover the SPM targets, not the Xcode app. Shared Sparkle release uses the exact release tag and checks marketing version; local release-local has no clean-tree/tag gate.

```text
Available recipes:
    default                  # List available commands
    archive platform="macos" # Regenerate the project, Archive, and verify its app/extension build identity.
    info                     # Show the UTC build preview, commit, dirty files, tag-at-HEAD and channel.

    [dev]
    build                    # Build every SPM target (Core, auditctlKit, auditctl, guest agent, protocol)
    test                     # Run the full SPM test suite (same as CI)
    clean                    # Remove SPM build output

    [ship]
    release version          # Tag v<version> and push it to trigger the release workflow (tag must match MARKETING_VERSION)
    release-local            # Build, sign, notarize and package the DMG locally (needs Developer ID + notary env)
```

## Orbari

Repository: https://github.com/AdamXweb/Orbari. Source audited: `94a3c03dc38b6d18fecd12a7143215197c5297d0`.

App CI builds macOS and iOS Simulator, runs the headless harness and local StoreKit tests. Shared iOS Release validation runs on PR/main; signed IPA export requires manual dispatch with the signed-archive checkbox. No macOS distribution workflow.

```text
Available recipes:
    default                  # Show the available commands.
    archive platform="macos" # Archive using the shared scheme identity and verify the completed archive.

    [dev]
    generate                 # Generate the Xcode project from project.yml
    info                     # What commit is this working tree, and is it dirty? (docs/VERSIONING.md §5)
    build                    # Build both platforms, unsigned (banner first)
    build-ios                # iOS Simulator build, unsigned
    build-mac                # macOS build, unsigned
    test                     # Headless Swift test suites (requires full Xcode).
```

## Validation

All eleven justfiles parse. Forty-four local reference-script checks passed: real clean/dirty/tagged/shallow/detached Git fixtures, one UTC capture, CI channel selection, Xcode derived plist capture and release redaction, Fastlane overrides and Archive verification. The shared pipeline test executes its real source guard against tagged, newer, dirty and detached Git fixtures. Shared action/workflow lint and YAML parsing pass. Lyrebird's required local Swift build and tests pass. Real OrgOrbari iOS Simulator and macOS builds passed and their plists carry the identical UTC stamp and ci channel. Orbari macOS Archive passed Organizer/app/extension verification with release redaction preserved. Lyrebird ran 371 tests with no failures. App workflow lint introduces no diagnostics compared with the audited main snapshots (existing custom runner labels/legacy shell warnings remain).

Build-identity fixture CI is not an Apple compile or a signed export. Live signing/notarization/App Store uploads were not executed for this audit.

Shared pipeline correction merged: https://github.com/privacykey/gh-workflows/pull/17 (`57d245db16e566c11d6ef66a6bb0bcd010e6bb12`). Portfolio callers pin this commit explicitly; v1 was not moved.

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
