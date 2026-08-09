---
name: yaml-infographic
description: Create consistent single-canvas infographics from a structured YAML information architecture and a versioned global visual style. Use when the user asks for an infographic, information graphic, social-media long image, process graphic, comparison graphic, timeline, data story, checklist, anatomy callout, or a YAML-planned single image in 1:1, 4:5, 9:16, 16:9, or A4 proportions. Supports baked visuals and text-free plates with exact editable overlays.
---

# YAML Infographic

Create one complete information graphic from a validated YAML contract. Keep the global visual identity separate from the single-canvas information architecture.

## Defaults

- Use `yaml_spec` planning and one of the bundled versioned profiles unless the user explicitly supplies another style. Pick by publishing surface: `global:paper_warm@1.0.0` for printed handouts and bright rooms, `global:tech_calm@1.0.0` for dark-room screens and social posts.
- Default to `plate` for Traditional Chinese, exact numbers, charts, dates, citations, formulas, maps, or content intended for later revision.
- Use `baked` only for low-density visual storytelling with short copy and no precision-critical data.
- Generate a single canvas, not a slide deck. Do not create a `slides` section.
- Keep every artifact under the active project directory.

## Global Style

A `global:<style_id>@<version>` reference resolves to `<style-id>.yaml` in this order:

1. `%USERPROFILE%\.agents\visual-styles\<style-id>.yaml`
2. `assets/<style-id>.yaml` bundled with this skill

Bundled profiles:

| Reference | File | Look | Golden sample |
|---|---|---|---|
| `global:paper_warm@1.0.0` | `paper-warm.yaml` | Warm paper, ink-grey text, amber keywords, red for the single top emphasis | **Not yet produced** |
| `global:tech_calm@1.0.0` | `tech-calm.yaml` | Near-black surfaces, ice-white text, orange keywords, yellow for the single top emphasis | `channel-style-tech-calm.png` |

Any profile declaring a matching `style.id`, `style.version`, and a complete `palette` is equally valid — nothing about a specific palette is hard-coded in the validator.

`paper_warm` has no golden sample yet, so a `spec.yaml` using it still has to point `design_system.golden_sample` at an existing image. Do not point it at the `tech_calm` sample: a near-black reference image will actively fight a warm-paper prompt. Produce a `paper_warm` sample first, or stay on `tech_calm` until one exists.

Use `assets/channel-style-tech-calm.png` as the bundled golden-sample fallback. Preserve near-black surfaces, ice-white text, orange keywords and signal lines, and yellow only for the single highest-priority emphasis. Explicit user or project styles override the default profile.

## Workflow

Run every command from the project directory that holds `spec.yaml`. `<SKILL_DIR>` is this skill's installed location — for example `%USERPROFILE%\.claude\skills\yaml-infographic` for Claude Code, or `%USERPROFILE%\.codex\skills\yaml-infographic` for Codex. When working inside the source repository instead, `<SKILL_DIR>` is `skills\yaml-infographic`.

1. Define the audience, purpose, one key message, publishing surface, and required aspect ratio.
2. Create `spec.yaml` from `assets/infographic-spec-template.yaml`.
3. Select the information relationship and matching layout from `references/layout-library.md`.
4. Separate exact facts from decorative copy. Add sources for statistics, dates, percentages, money, and externally verifiable claims.
5. Validate before generation:

   ```powershell
   python <SKILL_DIR>\scripts\validate_spec.py --spec .\spec.yaml
   ```

6. Compile and save the image prompt:

   ```powershell
   python <SKILL_DIR>\scripts\compile_prompt.py --spec .\spec.yaml
   ```

7. Generate the visual with built-in image generation. For `plate`, generate a text-free background and apply exact text, charts, or formulas afterward.
8. Inspect the original size and a social-thumbnail size. Regenerate or recompose failed regions instead of accepting tiny or incorrect text.
9. Verify declared outputs:

   ```powershell
   python <SKILL_DIR>\scripts\verify_output.py --spec .\spec.yaml --project-root .
   ```

10. Report the YAML, prompt record, final image, source plate or overlay, mode, dimensions, and style profile version.

## Output Policy

- `baked`: one final PNG/JPG/WebP; no `overlay_blocks`. Use only when all visible text may safely be regenerated.
- `plate`: a text-free plate, a final raster image, an SVG overlay source, and non-empty `overlay_blocks`.
- Do not claim that image generation produced editable SVG. In plate mode, SVG contains native overlay text, charts, and vector shapes; AI backgrounds remain raster assets.
- Split extremely tall or dense infographics into zones, generate plates per zone, and compose them locally.

## Precision Policy

- Render charts, tables, formulas, axes, maps, scales, and exact geometry natively in plate mode.
- Store exact numbers in `data_integrity.exact_numbers`; do not leave them only inside visible prose.
- Require a resolvable citation for every source-dependent exact number.
- Keep one `primary` emphasis per canvas so yellow remains a true priority signal.
- Require complete alt text and never use color as the only cue.

## References

- Read `references/schema.md` before authoring or changing YAML.
- Read `references/layout-library.md` before choosing a composition.
- Read `references/prompting.md` before image generation.
- Read `references/validation.md` before delivery.
