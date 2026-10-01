# Portfolio standards

For Apple app signing, read `docs/SIGNING.md`. The agreed Apple Developer
team is Adam Kostarelas (`6S9Q286XS9`) across AdamXweb, adamXbot and privacykey.
Keep the team in source project settings so regeneration preserves it, and
cover app, extension, helper and test targets in every build configuration.

For app versioning, build tracking and provenance, read `docs/VERSIONING.md`.
The agreed build number is `YYYY.MMDD.HHMM` in UTC. Keep marketing versions
hand-chosen and repository provenance in separate metadata. Existing epoch-based
pipeline defaults do not supersede this agreement.

Reusable reference code lives in `standards/versioning`. Run
the reference suites documented in `standards/versioning/README.md` after changing it.
