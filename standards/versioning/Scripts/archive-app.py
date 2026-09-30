#!/usr/bin/env python3
"""Regenerate if needed, archive with Xcode's normal version capture, then verify it.

This command creates an archive only. Export and upload remain separate actions.
"""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--platform")
parser.add_argument("--unsigned", action="store_true", help="Validate an archive without a signing identity")
parser.add_argument("--plan", action="store_true", help="Print the commands without running them")
args = parser.parse_args()
config = json.loads((root / "Config/ArchiveTargets.json").read_text())
platform = args.platform or config["defaultPlatform"]
if platform not in config["platforms"]:
    parser.error(f"Choose a supported platform: {', '.join(config['platforms'])}")
target = config["platforms"][platform]
commands = []
if config.get("spec"):
    commands.append(["xcodegen", "generate", "--spec", config["spec"]])
archive = root / "build" / (target["scheme"] + "-" + platform + ".xcarchive")
command = ["xcodebuild", "archive", "-project", config["project"], "-scheme", target["scheme"],
           "-configuration", "Release", "-destination", target["destination"], "-archivePath", str(archive)]
if args.unsigned:
    command.append("CODE_SIGNING_ALLOWED=NO")
else:
    command.append("-allowProvisioningUpdates")
    team = next((os.environ[name] for name in ("APPLE_TEAM_ID", "TEAM_ID", "FASTLANE_TEAM_ID")
                 if os.environ.get(name)), "")
    if team:
        if not re.fullmatch(r"[A-Z0-9]{10}", team):
            parser.error("Apple team ID must have 10 uppercase letters/digits")
        command.append("DEVELOPMENT_TEAM=" + team)
commands.append(command)
commands.append(["python3", str(Path(__file__).with_name("verify-archive.py")), str(archive)])
if args.plan:
    print(json.dumps(commands, indent=2))
else:
    env = dict(os.environ, BUILD_CHANNEL="release")
    for command in commands:
        subprocess.run(command, cwd=root, env=env, check=True)
    print(f"Archive ready: {archive}")
