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

Use `profile_ref: global:tech_calm@1.0.0`. Resolve it from the shared user profile first and use the bundled asset only as a fallback. Use `profile_ref: explicit` plus non-empty `overrides` when the user requests another style.

## Output contract

- `baked`: `final_path` and `prompt_record`; no plate, SVG overlay, or `overlay_blocks`.
- `plate`: `plate_path`, `overlay_path`, `final_path`, `prompt_record`, `background_text_policy: none`, and non-empty `overlay_blocks`.
- All paths must be relative to the project and must not contain `..`.
