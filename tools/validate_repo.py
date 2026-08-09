#!/usr/bin/env python3
import os
from pathlib import Path
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

style = yaml.safe_load((skill / "assets" / "tech-calm.yaml").read_text(encoding="utf-8"))
golden_sample = skill / "assets" / style.get("golden_sample", "")
if not golden_sample.is_file():
    raise SystemExit(f"Bundled golden sample does not exist: {golden_sample}")

forbidden = ("C:\\Users\\", "G:\\我的雲端硬碟", "gh" + "o_", "api" + "_key:", "pass" + "word:")
text_suffixes = {".md", ".py", ".ps1", ".yaml", ".yml", ".txt"}
for path in root.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in text_suffixes:
        continue
    text = path.read_text(encoding="utf-8")
    for marker in forbidden:
        if marker.lower() in text.lower():
            raise SystemExit(f"Potential private value in {path.relative_to(root)}: {marker}")

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
