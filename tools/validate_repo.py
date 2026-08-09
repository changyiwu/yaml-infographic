#!/usr/bin/env python3
import os
from pathlib import Path
import re
import subprocess
import sys

import yaml


root = Path(__file__).resolve().parents[1]
skill = root / "skills" / "yaml-infographic"

required = [
    root / "README.md",
    root / "LICENSE",
    root / "LICENSE-ASSETS.md",
    root / "requirements.txt",
    skill / "SKILL.md",
    skill / "agents" / "openai.yaml",
    skill / "assets" / "infographic-spec-template.yaml",
    skill / "assets" / "tech-calm.yaml",
    skill / "scripts" / "validate_spec.py",
    skill / "scripts" / "compile_prompt.py",
    skill / "scripts" / "verify_output.py",
    root / "tests" / "test_skill.py",
]
for path in required:
    if not path.is_file():
        raise SystemExit(f"Missing required file: {path.relative_to(root)}")

skill_text = (skill / "SKILL.md").read_text(encoding="utf-8")
if not skill_text.startswith("---\n") or "name: yaml-infographic" not in skill_text:
    raise SystemExit("Invalid SKILL.md frontmatter")

openai = yaml.safe_load((skill / "agents" / "openai.yaml").read_text(encoding="utf-8"))
prompt = openai.get("interface", {}).get("default_prompt", "")
if "$yaml-infographic" not in prompt:
    raise SystemExit("agents/openai.yaml default_prompt must mention $yaml-infographic")

# Every bundled style profile is checked, not just one hard-coded filename, so
# adding a profile needs no change here. The filename must match the style id
# because that is how `profile_ref` resolves to a file.
profiles = []
for candidate in sorted((skill / "assets").glob("*.yaml")):
    data = yaml.safe_load(candidate.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != "agent_visual_style_v1":
        continue
    profiles.append(candidate.name)
    style_id = (data.get("style") or {}).get("id")
    if not style_id:
        raise SystemExit(f"Style profile declares no style.id: {candidate.relative_to(root)}")
    expected_name = style_id.replace("_", "-") + ".yaml"
    if candidate.name != expected_name:
        raise SystemExit(f"Style profile {candidate.name} must be named {expected_name} to resolve")
    golden_sample = data.get("golden_sample") or ""
    if golden_sample and not (skill / "assets" / golden_sample).is_file():
        raise SystemExit(f"Golden sample declared by {candidate.name} does not exist: {golden_sample}")
if not profiles:
    raise SystemExit("No bundled style profile found")

# Drive letters are not hard-coded: any machine's home or cloud-drive path is
# rejected, and secrets must look like real values rather than the bare word.
# Patterns are written so this file does not trip its own scan.
forbidden = (
    (re.compile(r"[A-Za-z]:[\\/]Users[\\/]\S"), "本機使用者絕對路徑"),
    (re.compile(r"[A-Za-z]:[\\/]我的雲端硬碟"), "雲端硬碟絕對路徑"),
    (re.compile(r"gh[po]_[A-Za-z0-9]{20,}"), "GitHub token"),
    (re.compile(r"(?i)\bapi.?key\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{8,}"), "API key"),
    (re.compile(r"(?i)\bpassword\s*[:=]\s*[\"']?\S"), "password"),
)
text_suffixes = {".md", ".py", ".ps1", ".yaml", ".yml", ".txt"}
skip_dirs = {".git", "__pycache__", ".venv", "venv", "outputs", "output", "tmp"}
for path in root.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in text_suffixes:
        continue
    if skip_dirs.intersection(path.relative_to(root).parts):
        continue
    text = path.read_text(encoding="utf-8")
    for pattern, label in forbidden:
        if pattern.search(text):
            raise SystemExit(f"Potential private value in {path.relative_to(root)}: {label}")

env = os.environ.copy()
env["PYTHONUTF8"] = "1"

for spec in sorted((root / "examples").glob("*/spec.yaml")):
    result = subprocess.run(
        [sys.executable, str(skill / "scripts" / "validate_spec.py"), "--spec", str(spec)],
        cwd=root,
        env=env,
    )
    if result.returncode:
        raise SystemExit(result.returncode)

result = subprocess.run(
    [sys.executable, str(root / "tests" / "test_skill.py"), "--skill", str(skill)],
    cwd=root,
    env=env,
)
if result.returncode:
    raise SystemExit(result.returncode)

print("REPO VALID: yaml-infographic")
