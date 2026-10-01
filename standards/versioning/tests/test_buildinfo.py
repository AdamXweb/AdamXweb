#!/usr/bin/env python3
"""Run the real reference scripts against isolated repositories and a fixed UTC clock."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

kit = Path(__file__).resolve().parents[1]


def run(args, cwd, env):
    return subprocess.check_output(args, cwd=cwd, env=env, text=True)


with tempfile.TemporaryDirectory() as temporary:
    base = Path(temporary)
    repo = base / "app"
    shutil.copytree(kit, repo)
    # Git provenance includes only this fixture, never a caller's worktree/index.
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    clock = base / "clock"
    clock.mkdir()
    date = clock / "date"
    date.write_text("#!/bin/sh\n"
                    "[ \"$1\" = '-u' ] || exit 1\n"
                    "[ \"$2\" = '+%Y.%m%d.%H%M|%Y-%m-%dT%H:%M:%SZ' ] || exit 1\n"
                    "echo tick >> \"$CLOCK_CALLS\"\n"
                    "printf '%s\\n' '2026.1231.2359|2026-12-31T23:59:59Z'\n")
    date.chmod(0o755)
    env.update(PATH=str(clock) + os.pathsep + env["PATH"], CLOCK_CALLS=str(base / "ticks"),
               TZ="Australia/Melbourne", BUILD_CHANNEL="local", BUILD_PROVENANCE="full")

    def stamp(cwd=repo, **overrides):
        output = run(["bash", str(repo / "Scripts/buildinfo.sh")], cwd, dict(env, **overrides))
        return dict(line.split("=", 1) for line in output.splitlines())

    run(["git", "init", "-q"], repo, env)
    run(["git", "config", "user.name", "Versioning test"], repo, env)
    run(["git", "config", "user.email", "versioning@example.invalid"], repo, env)
    run(["git", "add", "."], repo, env)
    run(["git", "-c", "commit.gpgsign=false", "commit", "-qm", "Fixture"], repo, env)

    clean = stamp()
    assert clean["BUILD_NUMBER"] == "2026.1231.2359"
    assert clean["BUILD_TIMESTAMP"] == "2026-12-31T23:59:59Z"
    assert (base / "ticks").read_text().splitlines() == ["tick"], "Capture date once"
    assert clean["BUILD_DIRTY"] == "NO" and clean["BUILD_DIRTY_FILES"] == "0"
    assert len(clean["BUILD_SHA"]) == 8 and clean["BUILD_TAGGED"] == "NO"

    run(["git", "-c", "tag.gpgsign=false", "tag", "-a", "snapshot", "-m", "Snapshot"], repo, env)
    assert stamp()["BUILD_TAGGED"] == "NO", "Only a version tag marks a release"
    run(["git", "-c", "tag.gpgsign=false", "tag", "v1-preview"], repo, env)
    assert stamp()["BUILD_TAGGED"] == "NO", "A v-prefixed snapshot is not a release tag"
    run(["git", "-c", "tag.gpgsign=false", "tag", "-a", "v0.1.0", "-m", "Release"], repo, env)
    assert stamp()["BUILD_TAGGED"] == "YES"
    shallow = base / "shallow"
    run(["git", "clone", "-q", "--depth=1", "--no-tags", repo.as_uri(), str(shallow)], base, env)
    assert stamp(shallow)["BUILD_TAGGED"] == "NO", "Missing tag refs cannot be inferred from CI ref names"
    run(["git", "fetch", "-q", "--tags"], shallow, env)
    assert stamp(shallow)["BUILD_TAGGED"] == "YES"
    run(["git", "checkout", "-q", "--detach"], shallow, env)
    detached = stamp(shallow)
    assert detached["BUILD_BRANCH"] == "HEAD" and detached["BUILD_TAGGED"] == "YES"
    assert stamp(BUILD_CHANNEL="", CI="true")["BUILD_CHANNEL"] == "ci"
    assert stamp(BUILD_CHANNEL="xcode", GITHUB_ACTIONS="true")["BUILD_CHANNEL"] == "ci"
    assert stamp(BUILD_CHANNEL="local", CI="true")["BUILD_CHANNEL"] == "local"
    assert stamp(BUILD_CHANNEL="release", GITHUB_ACTIONS="true")["BUILD_CHANNEL"] == "release"

    untracked = repo / "new note.txt"
    untracked.write_text("first draft")
    dirty = stamp()
    assert dirty["BUILD_DIRTY"] == "YES" and dirty["BUILD_DIRTY_FILES"] == "1"
    assert dirty["BUILD_TAGGED"] == "YES", "Dirty files do not erase a tag at the base commit"
    assert dirty["BUILD_DIFF_ID"] and dirty["BUILD_DIFF_ID"] != "e3b0c442"
    untracked.write_text("second draft")
    assert stamp()["BUILD_DIFF_ID"] != dirty["BUILD_DIFF_ID"]
    untracked.unlink()
    (repo / "Config/Shared.xcconfig").write_text("MARKETING_VERSION = 0.2.0\n")
    assert stamp()["BUILD_DIRTY"] == "YES"

    minimal_env = {key: value for key, value in env.items() if key != "BUILD_PROVENANCE"}
    minimal_env["BUILD_CHANNEL"] = "release"
    output = run(["bash", str(repo / "Scripts/buildinfo.sh")], repo, minimal_env)
    release = dict(line.split("=", 1) for line in output.splitlines())
    for key in ["BUILD_SHA", "BUILD_BRANCH", "BUILD_DESCRIBE", "BUILD_DIFF_ID"]:
        assert release[key] == "", key
    assert release["BUILD_CHANNEL"] == "release"

    exported = base / "source export"
    exported.mkdir()
    missing = stamp(exported)
    assert missing["BUILD_SHA"] == "" and missing["BUILD_DIRTY"] == "NO"
    assert missing["BUILD_NUMBER"] == clean["BUILD_NUMBER"]

    marker = base / "evaluated"
    injected = dict(clean, BUILD_BRANCH=f"$(touch {marker})")
    info = "\n".join(f"{key}={value}" for key, value in injected.items())
    banner = run(["bash", str(repo / "Scripts/banner.sh"), "Fixture"], repo, dict(env, BUILD_INFO=info))
    assert "Fixture 0.2.0 (2026.1231.2359)" in banner
    assert injected["BUILD_BRANCH"] in banner and not marker.exists(), "Provenance is data"
    (repo / "Config/Shared.xcconfig").unlink()
    banner = run(["bash", str(repo / "Scripts/banner.sh"), "Fixture"], repo, env)
    assert "Fixture 0.0.0 (2026.1231.2359)" in banner

print("Build tracking reference passed: UTC identity, clean/tagged/dirty trees, redaction, exports, safe banner")
