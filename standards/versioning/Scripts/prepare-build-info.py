#!/usr/bin/env python3
"""Capture a scheme identity, then write derived source plists before Xcode signs them.

The scheme pre-action runs outside the build-phase sandbox and reads Git once.
Each shipping target consumes the same captured identity inside its sandbox.
Neither tracked plists nor signed products are modified.
"""
import os
from pathlib import Path
import plistlib
import re
import subprocess
import sys

PLIST_KEYS = {
    "BuildSHA": "BUILD_SHA", "BuildBranch": "BUILD_BRANCH",
    "BuildDirty": "BUILD_DIRTY", "BuildDirtyFiles": "BUILD_DIRTY_FILES",
    "BuildDiffID": "BUILD_DIFF_ID", "BuildDescribe": "BUILD_DESCRIBE",
    "BuildTagged": "BUILD_TAGGED", "BuildTimestamp": "BUILD_TIMESTAMP",
    "BuildChannel": "BUILD_CHANNEL",
}


def channel():
    requested = os.environ.get("BUILD_CHANNEL", "")
    if requested and requested != "xcode":
        return requested
    if os.environ.get("ACTION") == "install":
        return "release"
    if os.environ.get("GITHUB_ACTIONS") == "true" or os.environ.get("CI", "").lower() in ("true", "1", "yes"):
        return "ci"
    return "local"


def main():
    session = Path(os.environ["PROJECT_TEMP_DIR"]) / "BuildIdentity.plist"
    if sys.argv[1] == "session":
        # A failed capture must never leave the previous build's identity usable.
        session.unlink(missing_ok=True)
        root = Path(__file__).resolve().parents[1]
        env = dict(os.environ, BUILD_CHANNEL=channel())
        result = subprocess.run(["bash", str(Path(__file__).with_name("buildinfo.sh"))],
                                cwd=root, env=env, check=True, capture_output=True, text=True)
        sys.stderr.write(result.stderr)
        values = dict(line.split("=", 1) for line in result.stdout.splitlines())
        session.parent.mkdir(parents=True, exist_ok=True)
        session.write_bytes(plistlib.dumps(values))
        return

    if not session.is_file():
        raise RuntimeError("Build identity is missing. Build or Archive using a shared app scheme.")
    values = plistlib.loads(session.read_bytes())
    # A wrapper can capture once for multiple platform invocations. Only a
    # complete stamp overrides the session; xcconfig defaults are sentinels.
    if os.environ.get("BUILD_TIMESTAMP") and os.environ.get("BUILD_NUMBER") not in (None, "", "0"):
        values.update({key: os.environ.get(key, "") for key in values})
    build = os.environ.get("CURRENT_PROJECT_VERSION", "0")
    if build in ("", "0"):
        build = values["BUILD_NUMBER"]
    version = os.environ["MARKETING_VERSION"]
    if not re.fullmatch(r"[1-9][0-9]*(?:\.[0-9]+){0,2}", build):
        raise ValueError(f"Invalid build number: {build!r}")
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+){0,2}", version):
        raise ValueError(f"Invalid marketing version: {version!r}")
    # ACTION is authoritative in the target's archive build even if Xcode's
    # scheme pre-action did not expose its archive context.
    if os.environ.get("ACTION") == "install" and os.environ.get("BUILD_CHANNEL", "") in ("", "xcode"):
        values["BUILD_CHANNEL"] = "release"
        if os.environ.get("BUILD_PROVENANCE", "minimal") == "minimal":
            for key in ("BUILD_SHA", "BUILD_BRANCH", "BUILD_DESCRIBE", "BUILD_DIFF_ID"):
                values[key] = ""

    source = os.environ.get("BUILD_IDENTITY_SOURCE_PLIST", "")
    info = plistlib.loads(Path(source).read_bytes()) if source else {}
    info["CFBundleShortVersionString"] = version
    info["CFBundleVersion"] = build
    info.update({key: values.get(setting, "") for key, setting in PLIST_KEYS.items()})
    for key, setting in {
        "CFBundleName": "PRODUCT_NAME", "CFBundleIdentifier": "PRODUCT_BUNDLE_IDENTIFIER",
        "CFBundleExecutable": "EXECUTABLE_NAME", "CFBundlePackageType": "PRODUCT_BUNDLE_PACKAGE_TYPE",
    }.items():
        info.setdefault(key, os.environ.get(setting, f"$({setting})"))
    info.setdefault("CFBundleDevelopmentRegion", os.environ.get("DEVELOPMENT_LANGUAGE", "en"))
    info.setdefault("CFBundleInfoDictionaryVersion", "6.0")
    for setting, value in os.environ.items():
        if not setting.startswith("INFOPLIST_KEY_") or setting.endswith("_Generation"):
            continue
        key = setting.removeprefix("INFOPLIST_KEY_")
        if key.startswith("UISupportedInterfaceOrientations"):
            key = key.replace("_iPad", "~ipad").replace("_iPhone", "~iphone")
            info[key] = value.split()
        else:
            info[key] = {"YES": True, "NO": False}.get(value, value)
    if os.environ.get("PLATFORM_NAME") in ("iphoneos", "iphonesimulator", "appletvos", "appletvsimulator"):
        if os.environ.get("INFOPLIST_KEY_UIApplicationSceneManifest_Generation") == "YES":
            info.setdefault("UIApplicationSceneManifest", {"UIApplicationSupportsMultipleScenes": True, "UISceneConfigurations": {}})
        if os.environ.get("INFOPLIST_KEY_UILaunchScreen_Generation") == "YES":
            info.setdefault("UILaunchScreen", {})
        if info.get("CFBundlePackageType") == "APPL":
            info.setdefault("LSRequiresIPhoneOS", True)
    output = Path(os.environ["DERIVED_FILE_DIR"]) / "BuildIdentity-Info.plist"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(plistlib.dumps(info))
    print(f"{os.environ.get('PRODUCT_NAME', 'App')} {version} ({build})")
    print(f"Build provenance: channel={values['BUILD_CHANNEL']} dirty={values['BUILD_DIRTY']} "
          f"files={values['BUILD_DIRTY_FILES']} version-tag-at-HEAD={values['BUILD_TAGGED']} "
          f"timestamp={values['BUILD_TIMESTAMP']}")


if __name__ == "__main__":
    main()
