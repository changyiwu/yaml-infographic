#!/usr/bin/env python3
import argparse
from pathlib import Path
import re
import sys

try:
    import yaml
except ImportError:
    raise SystemExit("PyYAML is required: python -m pip install PyYAML")


RATIOS = {
    "1:1": 1.0,
    "4:5": 4 / 5,
    "9:16": 9 / 16,
    "16:9": 16 / 9,
    "A4_portrait": 210 / 297,
    "A4_landscape": 297 / 210,
}

PATTERN_LAYOUTS = {
    "focus": {"focus_hero"},
    "metric": {"single_metric"},
    "process": {"process_steps"},
    "cycle": {"cycle_loop"},
    "comparison": {"comparison_split", "matrix_quadrant"},
    "timeline": {"timeline"},
    "hierarchy": {"hierarchy_tree"},
    "classification": {"classification_grid"},
    "cause_effect": {"cause_effect_chain"},
    "relationship": {"relationship_map"},
    "data": {"data_story"},
    "list": {"ranked_list", "checklist"},
    "anatomy": {"anatomy_callout"},
    "story": {"modular_story"},
}

SECTION_REQUIRED = (
    "id", "order", "role", "layout_slot", "core_point", "visible_text",
    "items", "visual", "evidence_refs", "emphasis",
)


def add(errors, code, message):
    errors.append(f"{code}: {message}")


def require(mapping, key, where, errors):
    if not isinstance(mapping, dict) or key not in mapping:
        add(errors, "E_REQUIRED", f"{where}.{key} is required")


def text_length(value):
    if isinstance(value, str):
        return len(value.strip())
    if isinstance(value, dict):
        return sum(text_length(item) for item in value.values())
    if isinstance(value, list):
        return sum(text_length(item) for item in value)
    return 0


def safe_relative_path(raw):
    if not isinstance(raw, str) or not raw.strip():
        return False
    if Path(raw).is_absolute() or re.match(r"^[A-Za-z]:[\\/]", raw):
        return False
    return ".." not in Path(raw).parts


def load_style(skill_root, errors):
    global_path = Path.home() / ".agents" / "visual-styles" / "ai-agents-channel" / "tech-calm.yaml"
    fallback = skill_root / "assets" / "tech-calm.yaml"
    style_path = global_path if global_path.is_file() else fallback
    if not style_path.is_file():
        add(errors, "E_STYLE_NOT_FOUND", "global and bundled tech_calm profiles are missing")
        return None, None
    try:
        return yaml.safe_load(style_path.read_text(encoding="utf-8")), style_path
    except Exception as exc:
        add(errors, "E_STYLE_INVALID", f"cannot read {style_path}: {exc}")
        return None, style_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True)
    args = parser.parse_args()
    path = Path(args.spec)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    errors, warnings = [], []

    if not isinstance(data, dict):
        print("INVALID\n- E_ROOT: YAML root must be a mapping")
        return 1

    required_root = (
        "schema_version", "document", "canvas", "design_system",
        "information_architecture", "layout", "sections", "data_integrity",
        "accessibility", "output", "validation",
    )
    for key in required_root:
        if key not in data:
            add(errors, "E_REQUIRED", f"root.{key} is required")
    if "slides" in data:
        add(errors, "E_SLIDES_FORBIDDEN", "an infographic is one canvas and must not contain slides")
    if data.get("schema_version") != "yaml_infographic_v1":
        add(errors, "E_SCHEMA_VERSION", "schema_version must be yaml_infographic_v1")

    document = data.get("document") or {}
    for key in ("title", "audience", "purpose", "key_message", "language"):
        require(document, key, "document", errors)

    canvas = data.get("canvas") or {}
    for key in ("profile", "target_ratio", "width_px", "height_px", "safe_area_pct", "reading_direction"):
        require(canvas, key, "canvas", errors)
    ratio_name = canvas.get("target_ratio")
    expected_ratio = RATIOS.get(ratio_name)
    if expected_ratio is None:
        add(errors, "E_UNSUPPORTED_RATIO", f"unsupported target_ratio {ratio_name}")
    width, height = canvas.get("width_px"), canvas.get("height_px")
    if not isinstance(width, int) or not isinstance(height, int) or width <= 0 or height <= 0:
        add(errors, "E_CANVAS_DIMENSIONS", "width_px and height_px must be positive integers")
    elif expected_ratio and abs((width / height) - expected_ratio) / expected_ratio > 0.01:
        add(errors, "E_RATIO_DIMENSION_MISMATCH", f"{width}x{height} does not match {ratio_name}")
    if canvas.get("reading_direction") not in {"top_to_bottom", "left_to_right", "z_pattern", "center_out", "clockwise"}:
        add(errors, "E_READING_DIRECTION", "unsupported reading_direction")
    safe_area = canvas.get("safe_area_pct") or {}
    for side in ("left", "right", "top", "bottom"):
        value = safe_area.get(side) if isinstance(safe_area, dict) else None
        if not isinstance(value, (int, float)) or not 4 <= value <= 12:
            add(errors, "E_SAFE_AREA", f"canvas.safe_area_pct.{side} must be between 4 and 12")

    design = data.get("design_system") or {}
    for key in ("preset", "preset_version", "profile_ref", "golden_sample", "overrides"):
        require(design, key, "design_system", errors)
    profile_ref = design.get("profile_ref")
    if profile_ref == "global:tech_calm@1.0.0":
        if design.get("preset") != "tech_calm" or str(design.get("preset_version")) != "1.0.0":
            add(errors, "E_STYLE_VERSION", "tech_calm must use preset version 1.0.0")
        style_data, style_path = load_style(Path(__file__).resolve().parents[1], errors)
        if isinstance(style_data, dict):
            style = style_data.get("style") or {}
            palette = style_data.get("palette") or {}
            if style.get("id") != "tech_calm" or str(style.get("version")) != "1.0.0":
                add(errors, "E_STYLE_VERSION", f"resolved profile has wrong identity: {style_path}")
            expected = {
                "background": "#050505", "background_secondary": "#0B0B0B",
                "surface": "#202020", "text": "#F5F7FA",
                "keyword": "#FF6A00", "highlight": "#FFD400",
            }
            for key, value in expected.items():
                if str(palette.get(key, "")).upper() != value:
                    add(errors, "E_STYLE_PALETTE", f"tech_calm palette.{key} must be {value}")
    elif profile_ref == "explicit":
        if not isinstance(design.get("overrides"), dict) or not design.get("overrides"):
            add(errors, "E_STYLE_OVERRIDE", "explicit profile_ref requires non-empty overrides")
    else:
        add(errors, "E_STYLE_PROFILE", "profile_ref must be global:tech_calm@1.0.0 or explicit")
    golden = design.get("golden_sample")
    if safe_relative_path(golden):
        project_candidate = path.parent / golden
        skill_candidate = Path(__file__).resolve().parents[1] / golden
        if not project_candidate.is_file() and not skill_candidate.is_file():
            add(errors, "E_GOLDEN_SAMPLE", f"golden sample not found: {golden}")
    else:
        add(errors, "E_OUTPUT_PATH", "design_system.golden_sample must be a safe relative path")

    architecture = data.get("information_architecture") or {}
    for key in ("pattern", "density", "reading_path"):
        require(architecture, key, "information_architecture", errors)
    pattern = architecture.get("pattern")
    if pattern not in PATTERN_LAYOUTS:
        add(errors, "E_UNSUPPORTED_PATTERN", f"unsupported pattern {pattern}")
    if architecture.get("density") not in {"low", "medium", "high"}:
        add(errors, "E_DENSITY", "density must be low, medium, or high")

    layout = data.get("layout") or {}
    for key in ("id", "variant", "zones"):
        require(layout, key, "layout", errors)
    layout_id = layout.get("id")
    if pattern in PATTERN_LAYOUTS and layout_id not in PATTERN_LAYOUTS[pattern]:
        add(errors, "E_LAYOUT_PATTERN_MISMATCH", f"layout {layout_id} is not allowed for {pattern}")
    zones = layout.get("zones") if isinstance(layout.get("zones"), list) else []
    zone_ids = set()
    for index, zone in enumerate(zones, 1):
        if not isinstance(zone, dict) or not zone.get("id") or not isinstance(zone.get("rect_pct"), list) or len(zone["rect_pct"]) != 4:
            add(errors, "E_LAYOUT_ZONE", f"layout.zones[{index}] must have id and four rect_pct values")
            continue
        zone_ids.add(zone["id"])
        if any(not isinstance(value, (int, float)) or value < 0 or value > 100 for value in zone["rect_pct"]):
            add(errors, "E_LAYOUT_ZONE", f"layout.zones[{index}] contains invalid percentages")

    sections = data.get("sections")
    if not isinstance(sections, list) or not sections:
        add(errors, "E_SECTIONS", "sections must be a non-empty list")
        sections = []
    ids, orders, primary_count, total_items = [], [], 0, 0
    for index, section in enumerate(sections, 1):
        where = f"sections[{index}]"
        if not isinstance(section, dict):
            add(errors, "E_SECTION", f"{where} must be a mapping")
            continue
        for key in SECTION_REQUIRED:
            require(section, key, where, errors)
        ids.append(section.get("id"))
        orders.append(section.get("order"))
        if section.get("layout_slot") not in zone_ids:
            add(errors, "E_LAYOUT_SLOT", f"{where}.layout_slot does not resolve to a layout zone")
        if section.get("emphasis") not in {"primary", "secondary", "none"}:
            add(errors, "E_EMPHASIS", f"{where}.emphasis is invalid")
        if section.get("emphasis") == "primary":
            primary_count += 1
        items = section.get("items")
        if not isinstance(items, list):
            add(errors, "E_ITEMS", f"{where}.items must be a list")
        else:
            total_items += len(items)
        visual = section.get("visual") or {}
        for key in ("kind", "brief", "subject_count"):
            require(visual, key, f"{where}.visual", errors)
    if len(ids) != len(set(ids)):
        add(errors, "E_SECTION_ID", "section IDs must be unique")
    if orders != list(range(1, len(sections) + 1)):
        add(errors, "E_SECTION_ORDER", "section order must be sequential from 1")
    if primary_count > 1:
        add(errors, "E_PRIMARY_EMPHASIS", "only one section may use primary emphasis")

    if pattern == "process" and not 3 <= total_items <= 7:
        add(errors, "E_LAYOUT_BUDGET", "process requires three to seven items")
    if pattern == "cycle" and not 3 <= total_items <= 6:
        add(errors, "E_LAYOUT_BUDGET", "cycle requires three to six items")
    if pattern == "timeline" and not 3 <= total_items <= 8:
        add(errors, "E_LAYOUT_BUDGET", "timeline requires three to eight items")
    if layout_id == "comparison_split":
        groups = [section for section in sections if isinstance(section, dict) and section.get("role") == "comparison_group"]
        if len(groups) != 2 or any(not 2 <= len(group.get("items") or []) <= 5 for group in groups):
            add(errors, "E_LAYOUT_BUDGET", "comparison_split requires exactly two comparison_group sections with two to five items each")
    if layout_id == "matrix_quadrant":
        cells = [section for section in sections if isinstance(section, dict) and section.get("role") == "cell"]
        if len(cells) != 4:
            add(errors, "E_LAYOUT_BUDGET", "matrix_quadrant requires exactly four cell sections")

    integrity = data.get("data_integrity") or {}
    for key in ("facts_require_source", "exact_numbers", "citations", "datasets"):
        require(integrity, key, "data_integrity", errors)
    if integrity.get("facts_require_source") is not True:
        add(errors, "E_SOURCE_POLICY", "facts_require_source must be true")
    exact_numbers = integrity.get("exact_numbers") if isinstance(integrity.get("exact_numbers"), list) else []
    citations = integrity.get("citations") if isinstance(integrity.get("citations"), list) else []
    citation_ids = {item.get("id") for item in citations if isinstance(item, dict) and item.get("id")}
    if exact_numbers and not citations:
        add(errors, "E_DATA_SOURCE_REQUIRED", "exact_numbers require at least one citation")
    for index, number in enumerate(exact_numbers, 1):
        if not isinstance(number, dict):
            add(errors, "E_EXACT_NUMBER", f"exact_numbers[{index}] must be a mapping")
            continue
        for key in ("id", "value", "source_id"):
            require(number, key, f"exact_numbers[{index}]", errors)
        if number.get("source_id") not in citation_ids:
            add(errors, "E_DATA_SOURCE_REQUIRED", f"exact_numbers[{index}].source_id does not resolve")
    for index, dataset in enumerate(integrity.get("datasets") or [], 1):
        if not isinstance(dataset, dict):
            add(errors, "E_DATASET", f"datasets[{index}] must be a mapping")
            continue
        labels, values = dataset.get("labels"), dataset.get("values")
        if not isinstance(labels, list) or not isinstance(values, list) or len(labels) != len(values):
            add(errors, "E_DATASET_LENGTH", f"datasets[{index}] labels and values must have equal lengths")
    if pattern == "data" and not exact_numbers and not integrity.get("datasets"):
        add(errors, "E_DATA_REQUIRED", "data pattern requires exact_numbers or datasets")

    accessibility = data.get("accessibility") or {}
    if not str(accessibility.get("alt_text", "")).strip():
        add(errors, "E_ALT_TEXT", "accessibility.alt_text is required")
    if accessibility.get("color_not_only_cue") is not True:
        add(errors, "E_COLOR_CUE", "color_not_only_cue must be true")
    if not isinstance(accessibility.get("minimum_contrast_ratio"), (int, float)) or accessibility.get("minimum_contrast_ratio", 0) < 4.5:
        add(errors, "E_CONTRAST", "minimum_contrast_ratio must be at least 4.5")

    output = data.get("output") or {}
    for key in ("mode", "format", "final_path", "prompt_record"):
        require(output, key, "output", errors)
    mode = output.get("mode")
    if mode not in {"baked", "plate"}:
        add(errors, "E_OUTPUT_MODE", "output.mode must be baked or plate")
    if output.get("format") not in {"png", "jpg", "jpeg", "webp"}:
        add(errors, "E_OUTPUT_FORMAT", "output.format must be png, jpg, jpeg, or webp")
    for key in ("final_path", "prompt_record", "plate_path", "overlay_path"):
        if key in output and not safe_relative_path(output.get(key)):
            add(errors, "E_OUTPUT_PATH", f"output.{key} must be a safe project-relative path")
    overlay_blocks = output.get("overlay_blocks")
    if mode == "baked":
        if output.get("plate_path") or output.get("overlay_path") or overlay_blocks:
            add(errors, "E_BAKED_OVERLAY_FORBIDDEN", "baked output must not declare plate or overlay artifacts")
        if exact_numbers:
            warnings.append("W_BAKED_EXACT_DATA: verify every rendered number visually")
    if mode == "plate":
        if not output.get("plate_path") or not output.get("overlay_path") or not isinstance(overlay_blocks, list) or not overlay_blocks:
            add(errors, "E_PLATE_OVERLAY_REQUIRED", "plate output requires plate_path, overlay_path, and non-empty overlay_blocks")
        if output.get("background_text_policy") != "none":
            add(errors, "E_PLATE_TEXT_POLICY", "plate background_text_policy must be none")
        for index, block in enumerate(overlay_blocks or [], 1):
            if not isinstance(block, dict) or block.get("section_ref") not in ids or block.get("zone") not in zone_ids:
                add(errors, "E_OVERLAY_REFERENCE", f"overlay_blocks[{index}] has unresolved section_ref or zone")

    title_limit = 18 if mode == "baked" else 24
    if text_length(document.get("title")) > title_limit:
        add(errors, "E_TITLE_BUDGET", f"document.title exceeds {title_limit} characters for {mode}")
    total_copy = sum(text_length(section.get("visible_text")) + text_length(section.get("items")) for section in sections if isinstance(section, dict))
    copy_limit = 80 if mode == "baked" else 220
    if total_copy > copy_limit:
        add(errors, "E_COPY_BUDGET", f"visible copy exceeds {copy_limit} characters for {mode}")

    validation = data.get("validation") or {}
    if validation.get("profile") not in {"strict", "standard"}:
        add(errors, "E_VALIDATION_PROFILE", "validation.profile must be strict or standard")

    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        for warning in warnings:
            print(f"! {warning}")
        return 1
    print(f"VALID: {path} ({ratio_name}, {len(sections)} sections, mode={mode}, style={profile_ref})")
    for warning in warnings:
        print(f"! {warning}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
