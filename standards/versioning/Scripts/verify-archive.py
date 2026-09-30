#!/usr/bin/env python3
"""Verify an Xcode archive's version/build metadata and bundled extensions."""
import argparse
from datetime import datetime
from pathlib import Path
import plistlib
import re

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("archive", type=Path)
args = parser.parse_args()
archive = args.archive
metadata = plistlib.loads((archive / "Info.plist").read_bytes())["ApplicationProperties"]
app = archive / "Products" / metadata["ApplicationPath"]
main_plist = app / "Contents/Info.plist" if (app / "Contents/Info.plist").is_file() else app / "Info.plist"
main = plistlib.loads(main_plist.read_bytes())
build = main["CFBundleVersion"]
version = main["CFBundleShortVersionString"]
assert re.fullmatch(r"[0-9]{4}\.[0-9]{4}\.[0-9]{4}", build), f"Unexpected build format: {build}"
assert metadata["CFBundleVersion"] == build, "Organizer build differs from the app"
assert metadata["CFBundleShortVersionString"] == version, "Organizer version differs from the app"
assert datetime.strptime(main["BuildTimestamp"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y.%m%d.%H%M") == build
assert main["BuildChannel"] in ("release", "testflight")
if main["BuildChannel"] == "release":
    assert all(main.get(key, "") == "" for key in ("BuildSHA", "BuildBranch", "BuildDescribe", "BuildDiffID"))
plists = [main_plist]
for bundle in app.rglob("*.appex"):
    if "Frameworks" in bundle.relative_to(app).parts:
        continue
    path = bundle / "Contents/Info.plist" if (bundle / "Contents/Info.plist").is_file() else bundle / "Info.plist"
    plists.append(path)
for path in plists:
    info = plistlib.loads(path.read_bytes())
    assert info["CFBundleVersion"] == build, path
    assert info["CFBundleShortVersionString"] == version, path
    assert info["BuildTimestamp"] == main["BuildTimestamp"], path
    print(f"{path.relative_to(archive)}: {version} ({build})")
print("Archive verified: Organizer, app and extension identity; UTC timestamp and release provenance")
