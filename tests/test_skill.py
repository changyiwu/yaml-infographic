#!/usr/bin/env python3
import argparse
import copy
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from PIL import Image
import yaml


def run(command, expect=0, code=None):
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    result = subprocess.run(command, text=True, encoding="utf-8", capture_output=True, env=env)
    output = result.stdout + result.stderr
    if result.returncode != expect:
        raise AssertionError(f"command returned {result.returncode}, expected {expect}\n{output}")
    if code and code not in output:
        raise AssertionError(f"missing {code}\n{output}")
    return output


def write_spec(root, data):
    path = root / "spec.yaml"
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000), encoding="utf-8")
    return path


def create_image(path, size):
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, "#050505").save(path)


def create_outputs(root, data):
    output = data["output"]
    size = (data["canvas"]["width_px"], data["canvas"]["height_px"])
    create_image(root / output["final_path"], size)
    if output["mode"] == "plate":
        create_image(root / output["plate_path"], size)
        overlay = root / output["overlay_path"]
        overlay.parent.mkdir(parents=True, exist_ok=True)
        overlay.write_text('<svg xmlns="http://www.w3.org/2000/svg"></svg>', encoding="utf-8")


def set_baked(data, ratio, width, height):
    data["canvas"].update({"target_ratio": ratio, "width_px": width, "height_px": height})
    data["output"]["mode"] = "baked"
    for key in ("plate_path", "overlay_path", "background_text_policy", "overlay_blocks"):
        data["output"].pop(key, None)


def positive_case(skill, root, data, label):
    root.mkdir(parents=True)
    spec = write_spec(root, data)
    run([sys.executable, str(skill / "scripts" / "validate_spec.py"), "--spec", str(spec)], code="VALID:")
    run([sys.executable, str(skill / "scripts" / "compile_prompt.py"), "--spec", str(spec)], code="WROTE:")
    prompt_path = root / data["output"]["prompt_record"]
    prompt_text = prompt_path.read_text(encoding="utf-8")
    if str(Path.home()) in prompt_text or ":\\" in prompt_text:
        raise AssertionError(f"prompt record leaked an absolute user path: {prompt_path}")
    create_outputs(root, data)
    run([
        sys.executable, str(skill / "scripts" / "verify_output.py"),
        "--spec", str(spec), "--project-root", str(root),
    ], code="VALID:")
    print(f"PASS {label}")
    return data


def negative_case(skill, root, data, label, expected_code):
    root.mkdir(parents=True)
    spec = write_spec(root, data)
    run([sys.executable, str(skill / "scripts" / "validate_spec.py"), "--spec", str(spec)], expect=1, code=expected_code)
    print(f"PASS {label} -> {expected_code}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill", required=True)
    args = parser.parse_args()
    skill = Path(args.skill).resolve()
    template = yaml.safe_load((skill / "assets" / "infographic-spec-template.yaml").read_text(encoding="utf-8"))

    with tempfile.TemporaryDirectory(prefix="yaml-infographic-test-") as raw:
        base = Path(raw)

        square = copy.deepcopy(template)
        square["document"]["title"] = "YAML 五步工作流"
        set_baked(square, "1:1", 1600, 1600)
        positive_case(skill, base / "square-process-baked", square, "1:1 process baked")

        portrait = copy.deepcopy(template)
        positive_case(skill, base / "portrait-process-plate", portrait, "4:5 process plate")

        data_story = copy.deepcopy(template)
        data_story["document"]["title"] = "十二張簡報生成檢查"
        data_story["information_architecture"].update({"pattern": "data", "reading_path": "headline_to_metrics_to_takeaway"})
        data_story["layout"]["id"] = "data_story"
        data_story["sections"][1]["role"] = "metrics"
        data_story["sections"][1]["items"] = ["十二張簡報", "六個代理", "三個階段", "百分之百驗證"]
        data_story["data_integrity"]["citations"] = [{"id": "project", "label": "本次專案設定", "source": "本次專案設定"}]
        data_story["data_integrity"]["exact_numbers"] = [
            {"id": "slides", "value": 12, "unit": "張", "source_id": "project"},
            {"id": "agents", "value": 6, "unit": "個", "source_id": "project"},
            {"id": "phases", "value": 3, "unit": "個", "source_id": "project"},
            {"id": "verified", "value": "100%", "unit": "", "source_id": "project"},
        ]
        set_baked(data_story, "9:16", 1080, 1920)
        positive_case(skill, base / "mobile-data-baked", data_story, "9:16 data baked")

        override = copy.deepcopy(template)
        override["design_system"].update({
            "preset": "paper_editorial",
            "preset_version": "1.0.0",
            "profile_ref": "explicit",
            "overrides": {
                "palette": {"background": "#F2EBDD", "text": "#17304A", "highlight": "#B33A3A"},
                "materials": ["warm paper", "subtle ink texture"],
                "negative_prompt": ["No black technology background"],
            },
        })
        positive_case(skill, base / "explicit-style-plate", override, "explicit style override plate")

        bad_ratio = copy.deepcopy(square)
        bad_ratio["canvas"]["target_ratio"] = "4:5"
        negative_case(skill, base / "bad-ratio", bad_ratio, "ratio mutation", "E_RATIO_DIMENSION_MISMATCH")

        bad_pattern = copy.deepcopy(square)
        bad_pattern["information_architecture"]["pattern"] = "radar"
        negative_case(skill, base / "bad-pattern", bad_pattern, "pattern mutation", "E_UNSUPPORTED_PATTERN")

        bad_source = copy.deepcopy(data_story)
        bad_source["data_integrity"]["citations"] = []
        negative_case(skill, base / "bad-source", bad_source, "source mutation", "E_DATA_SOURCE_REQUIRED")

        bad_baked = copy.deepcopy(square)
        bad_baked["output"]["overlay_blocks"] = [{"id": "x"}]
        negative_case(skill, base / "bad-baked", bad_baked, "baked overlay mutation", "E_BAKED_OVERLAY_FORBIDDEN")

        bad_plate = copy.deepcopy(portrait)
        bad_plate["output"]["overlay_blocks"] = []
        negative_case(skill, base / "bad-plate", bad_plate, "plate overlay mutation", "E_PLATE_OVERLAY_REQUIRED")

        bad_order = copy.deepcopy(portrait)
        bad_order["sections"][1]["order"] = 3
        negative_case(skill, base / "bad-order", bad_order, "section order mutation", "E_SECTION_ORDER")

        bad_profile_ref = copy.deepcopy(portrait)
        bad_profile_ref["design_system"]["profile_ref"] = "global:TechCalm@1"
        negative_case(skill, base / "bad-profile-ref", bad_profile_ref, "profile ref format mutation", "E_STYLE_PROFILE")

        missing_profile = copy.deepcopy(portrait)
        missing_profile["design_system"].update({
            "preset": "no_such_style",
            "preset_version": "1.0.0",
            "profile_ref": "global:no_such_style@1.0.0",
        })
        negative_case(skill, base / "missing-profile", missing_profile, "unknown profile", "E_STYLE_NOT_FOUND")

        mismatched_preset = copy.deepcopy(portrait)
        mismatched_preset["design_system"]["preset"] = "paper_editorial"
        negative_case(skill, base / "mismatched-preset", mismatched_preset, "preset mismatch", "E_STYLE_VERSION")

        guarded_root = base / "output-guard"
        guarded_root.mkdir(parents=True)
        guarded_spec = write_spec(guarded_root, copy.deepcopy(template))
        outside_target = base / "outside-prompt.md"
        run([
            sys.executable,
            str(skill / "scripts" / "compile_prompt.py"),
            "--spec",
            str(guarded_spec),
            "--output",
            str(outside_target),
        ], expect=1, code="Unsafe output path")
        if outside_target.exists():
            raise AssertionError("unsafe --output target was written")
        print("PASS output path guard -> Unsafe output path")

    print("ALL YAML INFOGRAPHIC TESTS PASSED")


if __name__ == "__main__":
    main()
