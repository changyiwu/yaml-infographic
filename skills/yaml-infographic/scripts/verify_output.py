#!/usr/bin/env python3
import argparse
from pathlib import Path
import sys

try:
    import yaml
except ImportError:
    raise SystemExit("PyYAML is required: python -m pip install PyYAML")

try:
    from PIL import Image
except ImportError:
    raise SystemExit("Pillow is required: python -m pip install Pillow")


RATIOS = {
    "1:1": 1.0,
    "4:5": 4 / 5,
    "9:16": 9 / 16,
    "16:9": 16 / 9,
    "A4_portrait": 210 / 297,
    "A4_landscape": 297 / 210,
}


def add(errors, code, message):
    errors.append(f"{code}: {message}")


def resolve_under(root, raw, errors, label):
    if not raw:
        add(errors, "E_OUTPUT_DECLARATION", f"{label} is not declared")
        return None
    target = (root / raw).resolve()
    resolved_root = root.resolve()
    if target != resolved_root and resolved_root not in target.parents:
        add(errors, "E_OUTPUT_PATH", f"{label} escapes project root")
        return None
    return target


def inspect_image(path, width, height, expected_ratio, errors, label):
    if not path or not path.is_file():
        add(errors, "E_OUTPUT_MISSING", f"{label} is missing: {path}")
        return None
    try:
        with Image.open(path) as image:
            actual = image.size
    except Exception as exc:
        add(errors, "E_OUTPUT_IMAGE", f"cannot read {label}: {exc}")
        return None
    if actual != (width, height):
        add(errors, "E_OUTPUT_DIMENSIONS", f"{label} is {actual[0]}x{actual[1]}, expected {width}x{height}")
    actual_ratio = actual[0] / actual[1]
    if abs(actual_ratio - expected_ratio) / expected_ratio > 0.01:
        add(errors, "E_OUTPUT_RATIO", f"{label} ratio does not match the YAML")
    return actual


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True)
    parser.add_argument("--project-root")
    parser.add_argument("--output-dir", help="Alias for --project-root for test harnesses")
    args = parser.parse_args()

    spec_path = Path(args.spec)
    data = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    root = Path(args.output_dir or args.project_root or spec_path.parent)
    canvas = data.get("canvas") or {}
    output = data.get("output") or {}
    errors = []
    width, height = canvas.get("width_px"), canvas.get("height_px")
    expected_ratio = RATIOS.get(canvas.get("target_ratio"))
    if not isinstance(width, int) or not isinstance(height, int) or expected_ratio is None:
        add(errors, "E_CANVAS", "canvas dimensions or target_ratio are invalid")

    final_path = resolve_under(root, output.get("final_path"), errors, "final_path")
    final_size = inspect_image(final_path, width, height, expected_ratio, errors, "final image") if expected_ratio else None

    prompt_path = resolve_under(root, output.get("prompt_record"), errors, "prompt_record")
    if prompt_path and not prompt_path.is_file():
        add(errors, "E_PROMPT_RECORD", f"prompt record is missing: {prompt_path}")

    mode = output.get("mode")
    if mode == "baked":
        if output.get("plate_path") or output.get("overlay_path") or output.get("overlay_blocks"):
            add(errors, "E_BAKED_OVERLAY_FORBIDDEN", "baked output declares plate or overlay artifacts")
    elif mode == "plate":
        plate_path = resolve_under(root, output.get("plate_path"), errors, "plate_path")
        overlay_path = resolve_under(root, output.get("overlay_path"), errors, "overlay_path")
        plate_size = inspect_image(plate_path, width, height, expected_ratio, errors, "plate image") if expected_ratio else None
        if final_size and plate_size and final_size != plate_size:
            add(errors, "E_PLATE_FINAL_SIZE", "plate and final image dimensions differ")
        if overlay_path and (not overlay_path.is_file() or overlay_path.suffix.lower() != ".svg"):
            add(errors, "E_OVERLAY_MISSING", f"SVG overlay is missing: {overlay_path}")
        if not isinstance(output.get("overlay_blocks"), list) or not output.get("overlay_blocks"):
            add(errors, "E_PLATE_OVERLAY_REQUIRED", "plate output requires overlay_blocks")
    else:
        add(errors, "E_OUTPUT_MODE", f"unsupported mode {mode}")

    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"VALID: {final_path} ({width}x{height}, {canvas.get('target_ratio')}, mode={mode})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
