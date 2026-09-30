#!/usr/bin/env python3
"""Check archive signing defaults and Organizer/extension verification."""
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import tempfile

kit = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory).resolve()
    shutil.copytree(kit / "Scripts", root / "Scripts")
    (root / "Config").mkdir()
    (root / "Config/ArchiveTargets.json").write_text(json.dumps({
        "project": "App/Fixture.xcodeproj", "spec": "App/project.yml", "defaultPlatform": "macos",
        "platforms": {"macos": {"scheme": "Fixture", "destination": "generic/platform=macOS"}},
    }))
    runner = root / "Scripts/archive-app.py"
    env = dict(os.environ, APPLE_TEAM_ID="ABCDEFGHIJ")
    commands = json.loads(subprocess.check_output(["python3", str(runner), "--plan"], env=env))
    assert commands[0] == ["xcodegen", "generate", "--spec", "App/project.yml"]
    assert "-allowProvisioningUpdates" in commands[1] and "DEVELOPMENT_TEAM=ABCDEFGHIJ" in commands[1]
    assert str(root / "build/Fixture-macos.xcarchive") in commands[1]
    assert not any(argument.startswith(("BUILD_NUMBER=", "CURRENT_PROJECT_VERSION=")) for argument in commands[1])
    unsigned = json.loads(subprocess.check_output(["python3", str(runner), "--unsigned", "--plan"], env=env))
    assert "CODE_SIGNING_ALLOWED=NO" in unsigned[1] and "-allowProvisioningUpdates" not in unsigned[1]
    failure = subprocess.run(["python3", str(runner), "--plan"], env=dict(env, APPLE_TEAM_ID="invalid"), capture_output=True)
    assert failure.returncode != 0
    archive = root / "Fixture.xcarchive"
    app = archive / "Products/Applications/Fixture.app"
    app.mkdir(parents=True)
    identity = {"CFBundleVersion": "2026.0930.1234", "CFBundleShortVersionString": "0.1.0",
                "BuildTimestamp": "2026-09-30T12:34:56Z", "BuildChannel": "release"}
    (archive / "Info.plist").write_bytes(plistlib.dumps({"ApplicationProperties": {
        "ApplicationPath": "Applications/Fixture.app", "CFBundleVersion": identity["CFBundleVersion"],
        "CFBundleShortVersionString": identity["CFBundleShortVersionString"],
    }}))
    (app / "Info.plist").write_bytes(plistlib.dumps(identity))
    extension = app / "PlugIns/FixtureWidget.appex"
    extension.mkdir(parents=True)
    (extension / "Info.plist").write_bytes(plistlib.dumps(identity))
    resources = extension / "LibraryResources.bundle"
    resources.mkdir()
    (resources / "Info.plist").write_bytes(plistlib.dumps({"CFBundleIdentifier": "library.resources"}))
    verify = ["python3", str(root / "Scripts/verify-archive.py"), str(archive)]
    subprocess.run(verify, check=True)
    (extension / "Info.plist").write_bytes(plistlib.dumps(dict(identity, CFBundleVersion="1")))
    failure = subprocess.run(verify, capture_output=True)
    assert failure.returncode != 0
print("Archive checks passed: signing defaults, automatic capture, Organizer/extension parity")
