# YAML Infographic Schema

Use `yaml_infographic_v1` for one information-rich canvas. Do not add `slides`.

## Root blocks

- `document`: audience, purpose, key message, language.
- `canvas`: profile, aspect ratio, dimensions, safe area, reading direction.
- `design_system`: versioned global profile or explicit override.
- `information_architecture`: semantic pattern, density, reading path.
- `layout`: one controlled composition and percentage zones.
- `sections`: ordered content blocks.
- `data_integrity`: exact numbers, citations, datasets.
- `accessibility`: alt text, contrast, non-color cues.
- `output`: baked or plate artifact contract.
- `validation`: fixed validation profile; it cannot disable hard checks.

## Section contract

Every section requires `id`, `order`, `role`, `layout_slot`, `core_point`, `visible_text`, `items`, `visual`, `evidence_refs`, and `emphasis`.

- Keep IDs unique and orders sequential from 1.
- Use `primary` emphasis at most once.
- Put verifiable numbers in `data_integrity.exact_numbers` and reference citations by ID.
- Keep zones as percentages; never store agent-specific absolute paths.

## Style profile

`profile_ref` accepts two forms:

- `global:<style_id>@<major.minor.patch>` — a named, versioned profile. `style_id` is lowercase with underscores. `design_system.preset` and `preset_version` must repeat the same id and version.
- `explicit` — an inline style, which requires non-empty `overrides`.

A `global:` reference resolves to `<style_id>.yaml` with underscores turned into hyphens, searched in this order:

1. `~/.agents/visual-styles/<file>.yaml`
2. `assets/<file>.yaml` bundled with this skill

The resolved profile must declare `style.id` and `style.version` matching the reference, plus a `palette` defining every required role — `background`, `background_secondary`, `surface`, `text`, `keyword`, `highlight` — each as a `#RRGGBB` value. **Validation checks structure, not specific colours**, so any palette may be used as long as every role is present and well-formed.

The bundled `tech_calm` profile is one such profile, not a hard-coded requirement.

## Output contract

- `baked`: `final_path` and `prompt_record`; no plate, SVG overlay, or `overlay_blocks`.
- `plate`: `plate_path`, `overlay_path`, `final_path`, `prompt_record`, `background_text_policy: none`, and non-empty `overlay_blocks`.
- All paths must be relative to the project and must not contain `..`.
