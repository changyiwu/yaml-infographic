# Infographic Validation

Validate in this order:

1. Schema, enums, unique section IDs, sequential order, and layout compatibility.
2. Canvas dimensions, ratio tolerance, safe area, reading direction, and social UI zones.
3. Content budget, one primary emphasis, section item limits, and readable thumbnail scale.
4. Exact-number source links, dataset lengths, units, and `as_of` dates for changing data.
5. Resolvable style profile version, golden sample, rounded typography, contrast, and non-color cues.
6. Baked or plate artifact contract and project-relative safe paths.
7. Final raster dimensions and ratio; for plate, verify plate and final image match.
8. Visual inspection at full size and approximately 25% thumbnail scale.

Reject:

- `slides` or slide-deck fields.
- Ratio and pixel-dimension mismatch.
- Unsupported information patterns or layouts.
- Baked output with overlays, precision-critical data, or excessive copy.
- Plate output without a text-free plate, SVG overlay source, and overlay blocks.
- Exact source-dependent numbers without citations.
- More than one `primary` emphasis.
- Absolute paths, parent traversal, or outputs outside the project.
- AI-generated charts, maps, formulas, axes, or exact geometry presented as verified data.
