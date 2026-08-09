#!/usr/bin/env python3
import argparse
from pathlib import Path
import re
import sys

try:
    import yaml
except ImportError:
    raise SystemExit("PyYAML is required: python -m pip install PyYAML")


PROFILE_REF_PATTERN = re.compile(r"^global:([a-z][a-z0-9_]*)@(\d+\.\d+\.\d+)$")

# Used only when a profile declares no typography or emphasis of its own.
DEFAULT_TYPOGRAPHY = (
    "bold rounded Traditional Chinese, thick even strokes, soft terminals, generous counters, "
    "low corner sharpness. Avoid condensed, angular, stencil, or mechanical Chinese type."
)
DEFAULT_EMPHASIS = (
    "Use the keyword colour for keywords and signal paths; reserve the highlight colour for the "
    "single primary emphasis."
)


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
    profile_ref = design.get("profile_ref")
    if profile_ref == "explicit":
        return {"style": {"id": "explicit"}, **(design.get("overrides") or {})}, "explicit overrides"
    match = PROFILE_REF_PATTERN.match(profile_ref) if isinstance(profile_ref, str) else None
    if not match:
        raise SystemExit(f"Unsupported profile_ref: {profile_ref}")
    filename = match.group(1).replace("_", "-") + ".yaml"
    global_path = Path.home() / ".agents" / "visual-styles" / filename
    fallback = skill_root / "assets" / filename
    path = global_path if global_path.is_file() else fallback
    if not path.is_file():
        raise SystemExit(f"Style profile not found: {filename}")
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
    # For `explicit`, load_style already flattens overrides onto the style mapping,
    # so every lookup below reads from one place regardless of profile kind.
    palette = style.get("palette") or {}
    materials = style.get("materials") or []
    negative = style.get("negative_prompt") or []
    typography = style.get("typography") or {}
    emphasis = style.get("emphasis") or {}
    composition = style.get("composition") or {}

    # Image models read the compiled prompt, so a profile may supply `prompt_en`
    # for wording sent to the model and keep font_feel/avoid as human-facing notes.
    typography_line = typography.get("prompt_en") or " ".join(
        part for part in (
            typography.get("font_feel"),
            f"Avoid {typography['avoid']}." if typography.get("avoid") else None,
        ) if part
    ) or DEFAULT_TYPOGRAPHY
    emphasis_line = " ".join(
        str(value) for value in (emphasis.get("keyword"), emphasis.get("priority")) if value
    ) or DEFAULT_EMPHASIS
    character_line = ", ".join(str(item) for item in composition.get("character") or [])
    composition_rules = [str(rule) for rule in composition.get("rules") or []]

    # The safe area used to be dumped as a raw mapping, which an image model has
    # no reason to act on. State it as an instruction, and say what counts as a
    # violation — shadows and background accents are the usual offenders.
    safe = canvas.get("safe_area_pct") or {}
    safe_line = (
        f"Safe area (hard requirement): keep the outer {safe.get('left')}% of the width completely "
        f"empty on the left and {safe.get('right')}% on the right; keep the top {safe.get('top')}% "
        f"and the bottom {safe.get('bottom')}% of the height completely empty. Nothing may enter "
        f"these margins — not lettering, cards, icons, connectors, drop shadows, or background "
        f"accents. Compose the artwork smaller rather than letting anything touch the edge."
    )

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

Canvas: {canvas['width_px']}x{canvas['height_px']} px, ratio {canvas['target_ratio']}, reading direction {canvas['reading_direction']}.
{safe_line}
Information architecture: pattern={architecture['pattern']}, density={architecture['density']}, reading path={architecture['reading_path']}.
Layout: id={layout['id']}, variant={layout['variant']}, zones={layout['zones']}.

Sections:
{chr(10).join(section_lines)}

Style profile: {design['profile_ref']} ({style_source}).
Palette: {palette}.
Materials: {materials}.
Typography: {typography_line}
Emphasis: {emphasis_line}
Composition character: {character_line}.
Composition rules: {chr(10).join('- ' + rule for rule in composition_rules)}

Output mode: {mode}.
{mode_rule}

Negative constraints: {'; '.join(str(item) for item in negative)}
"""

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(prompt, encoding="utf-8")
    print(f"WROTE: {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
