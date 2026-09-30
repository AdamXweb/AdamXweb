#!/usr/bin/env python3
"""Exercise scheme capture and target plist preparation with real reference scripts."""
import os
from pathlib import Path
import plistlib
import re
import shutil
import subprocess
import tempfile

kit = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    shutil.copytree(kit / "Scripts", root / "Scripts")
    script = root / "Scripts/prepare-build-info.py"
    env = dict(os.environ, PROJECT_TEMP_DIR=str(root / "project"), DERIVED_FILE_DIR=str(root / "target"),
               MARKETING_VERSION="0.1.0", CURRENT_PROJECT_VERSION="0", BUILD_NUMBER="0",
               BUILD_TIMESTAMP="", BUILD_CHANNEL="xcode", PRODUCT_NAME="Fixture",
               PRODUCT_BUNDLE_IDENTIFIER="example.fixture", EXECUTABLE_NAME="Fixture",
               PRODUCT_BUNDLE_PACKAGE_TYPE="APPL", PLATFORM_NAME="iphoneos", ACTION="install",
               INFOPLIST_KEY_UILaunchScreen_Generation="YES")
    env.pop("BUILD_PROVENANCE", None)
    subprocess.run(["python3", str(script), "session"], env=env, check=True)
    values = plistlib.loads((root / "project/BuildIdentity.plist").read_bytes())
    assert re.fullmatch(r"[0-9]{4}\.[0-9]{4}\.[0-9]{4}", values["BUILD_NUMBER"])
    assert values["BUILD_CHANNEL"] == "release"
    for name, source in [("App", {"NSCameraUsageDescription": "Keep this permission", "CFBundleDocumentTypes": [{"CFBundleTypeName": "Fixture"}]}),
                         ("Extension", {"NSExtension": {"NSExtensionPointIdentifier": "com.apple.share-services"}})]:
        path = root / (name + ".plist")
        path.write_bytes(plistlib.dumps(source))
        target_env = dict(env, BUILD_IDENTITY_SOURCE_PLIST=str(path), DERIVED_FILE_DIR=str(root / name))
        subprocess.run(["python3", str(script), "plist"], env=target_env, check=True)
        actual = plistlib.loads((root / name / "BuildIdentity-Info.plist").read_bytes())
        assert all(actual[key] == value for key, value in source.items())
        assert actual["CFBundleVersion"] == values["BUILD_NUMBER"]
        assert actual["CFBundleShortVersionString"] == "0.1.0"
        assert actual["BuildTimestamp"] == values["BUILD_TIMESTAMP"]
        assert actual["BuildChannel"] == "release" and actual["BuildSHA"] == ""
        assert actual["CFBundleExecutable"] == "Fixture" and "UILaunchScreen" in actual
    # A complete wrapper stamp wins even when a second platform captures later.
    env.update(BUILD_NUMBER="2026.0930.0000", CURRENT_PROJECT_VERSION="2026.0930.0000",
               BUILD_TIMESTAMP="2026-09-30T00:00:00Z", BUILD_CHANNEL="testflight",
               BUILD_SHA="12345678", BUILD_BRANCH="feature/fixture", BUILD_DIRTY="NO",
               BUILD_DIRTY_FILES="0", BUILD_DIFF_ID="", BUILD_DESCRIBE="fixture", BUILD_TAGGED="NO")
    subprocess.run(["python3", str(script), "plist"], env=env, check=True)
    actual = plistlib.loads((root / "target/BuildIdentity-Info.plist").read_bytes())
    assert actual["CFBundleVersion"] == "2026.0930.0000" and actual["BuildSHA"] == "12345678"
    assert actual["BuildTimestamp"] == "2026-09-30T00:00:00Z"
    # Invalid sentinels/marketing values fail before Xcode processes the plist.
    env["MARKETING_VERSION"] = "1.0-beta"
    failure = subprocess.run(["python3", str(script), "plist"], env=env, capture_output=True)
    assert failure.returncode != 0
    # If capture fails, the previous session cannot silently stamp a new archive.
    (root / "Scripts/buildinfo.sh").write_text("exit 1\n")
    failure = subprocess.run(["python3", str(script), "session"], env=env, capture_output=True)
    assert failure.returncode != 0 and not (root / "project/BuildIdentity.plist").exists()
    failure = subprocess.run(["python3", str(script), "plist"], env=env, capture_output=True)
    assert failure.returncode != 0 and b"Build identity is missing" in failure.stderr
print("Xcode identity passed: Archive capture, bundled target parity, metadata preservation, overrides")
