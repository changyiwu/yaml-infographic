#!/usr/bin/env python3
import argparse
from pathlib import Path

try:
    import yaml
except ImportError:
    raise SystemExit("PyYAML is required: python -m pip install PyYAML")


def flatten_text(value):
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        result = []
        for item in value.values():
            result.extend(flatten_text(item))
        return result
    if isinstance(value, list):
        result = []
        for item in value:
            result.extend(flatten_text(item))
        return result
    return []


def load_style(skill_root, design):
    if design.get("profile_ref") == "explicit":
        return {"style": {"id": "explicit"}, **(design.get("overrides") or {})}, "explicit overrides"
    global_path = Path.home() / ".agents" / "visual-styles" / "ai-agents-channel" / "tech-calm.yaml"
    fallback = skill_root / "assets" / "tech-calm.yaml"
    path = global_path if global_path.is_file() else fallback
    source_label = "global profile" if path == global_path else "bundled fallback"
    return yaml.safe_load(path.read_text(encoding="utf-8")), source_label


def safe_target(spec_path, raw):
    raw_path = Path(raw)
    target = raw_path if raw_path.is_absolute() else spec_path.parent / raw_path
    resolved_parent = spec_path.parent.resolve()
    resolved = target.resolve()
    if resolved != resolved_parent and resolved_parent not in resolved.parents:
        raise SystemExit(f"Unsafe output path: {raw}")
    return target


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()

    spec_path = Path(args.spec)
    data = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    design = data.get("design_system") or {}
    style, style_source = load_style(Path(__file__).resolve().parents[1], design)
    output = data.get("output") or {}
    target = safe_target(spec_path, args.output or output["prompt_record"])

    canvas = data["canvas"]
    architecture = data["information_architecture"]
    layout = data["layout"]
    mode = output["mode"]
    palette = style.get("palette") or (style.get("overrides") or {}).get("palette") or design.get("overrides", {}).get("palette", {})
    materials = style.get("materials") or design.get("overrides", {}).get("materials", [])
    negative = style.get("negative_prompt") or design.get("overrides", {}).get("negative_prompt", [])

    section_lines, exact_text = [], []
    for section in data["sections"]:
        visible = flatten_text(section.get("visible_text")) + flatten_text(section.get("items"))
        exact_text.extend(visible)
        section_lines.append(
            f"- {section['order']}. {section['id']} ({section['role']}, zone={section['layout_slot']}, "
            f"emphasis={section['emphasis']}): {section['core_point']}; visual={section['visual']['brief']}; "
            f"subjects={section['visual']['subject_count']}; items={section.get('items', [])}"
        )

    if mode == "baked":
        mode_rule = (
            "Render only the following exact quoted text and add no other characters: "
            + " | ".join(f'\"{item}\"' for item in exact_text if item)
        )
    else:
        mode_rule = (
            "Generate a complete text-free designed plate. Reserve the declared zones but include no letters, "
            "numbers, labels, logos, watermarks, fake charts, or UI mockups. Exact content will be added as a native overlay."
        )

    prompt = f"""# Compiled Infographic Prompt

Create the infographic itself, not a screen, poster mockup, laptop, or presentation display.

Canvas: {canvas['width_px']}x{canvas['height_px']} px, ratio {canvas['target_ratio']}, safe area {canvas['safe_area_pct']}, reading direction {canvas['reading_direction']}.
Information architecture: pattern={architecture['pattern']}, density={architecture['density']}, reading path={architecture['reading_path']}.
Layout: id={layout['id']}, variant={layout['variant']}, zones={layout['zones']}.

Sections:
{chr(10).join(section_lines)}

Style profile: {design['profile_ref']} ({style_source}).
Palette: {palette}.
Materials: {materials}.
Typography: bold rounded Traditional Chinese, thick even strokes, soft terminals, generous counters, low corner sharpness. Avoid condensed, angular, stencil, or mechanical Chinese type.
Emphasis: orange for keywords and signal paths; yellow only for the single primary emphasis.

Output mode: {mode}.
{mode_rule}

Negative constraints: {'; '.join(str(item) for item in negative)}
"""

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(prompt, encoding="utf-8")
    print(f"WROTE: {target}")


if __name__ == "__main__":
    main()
