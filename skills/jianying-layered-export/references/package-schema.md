# Portable package contract (schemaVersion 1)

This is an interchange and validation contract for this skill, not Jianying's native schema. Adapt the current project's exporter into it; do not hard-code the historical episode. The package root contains `manifest.json`, `draft_content.json` and local media. Additional cover images, notes and source files are allowed. The installer rebases portable paths only after this package passes verification.

The default skill task ends after writing and delivering the package. Use this schema to build it; run the checks below only when the user explicitly requests review. Missing native evidence does not prevent an export-only delivery. Report export completion separately from review, which remains `not_performed` until requested and performed.

```json
{
  "schemaVersion": 1,
  "project": {"name": "Example", "width": 1920, "height": 1080, "fps": 30, "durationUs": 5000000},
  "media": [{"path": "media/left.mov", "bytes": 1234, "sha256": "<64 hex digits>"}],
  "panels": [{"scene": "C01", "id": "left", "label": "Left demo"}],
  "sources": [{"scene": "C01", "objects": [{"id": "demo", "owner": "left"}]}],
  "segments": [{"id": "native-segment-id", "scene": "C01", "role": "graphics", "owner": "left", "sourceObjectIds": ["demo"]}]
}
```

This abbreviated example is not a complete runnable draft. Every native segment must have exactly one manifest entry, and every nonempty referenced local material path, including fonts nested in JSON text content, must be in `media`. A declared system-font dependency may leave file paths empty; it is not a bundled or verified font.

## Manifest fields

- `project`: nonempty `name`, positive integer `width`, `height`, `durationUs`; positive numeric `fps`. They must match the draft's `name`, `canvas_config`, `duration` and `fps`. Timeline units are integer microseconds; comparison permits 1 µs rounding at boundaries. Duration equals the greatest segment end; trailing intentional silence needs a corresponding timeline segment.
- `media`: each local media/font path, exact byte length and SHA-256. Paths are relative to the package root; no drive letters, URLs, parent traversal or symlink escape. `/` is preferred; `\` is accepted. Empty native optional path fields are ignored. Sidecar documentation not referenced as draft material need not be listed.
- `panels`: independent large-box owners, uniquely identified by `(scene,id)`. IDs are stable semantic IDs and cannot be `shared`; labels are optional. Panels with text only are valid. The manifest is a description of ownership, not a request to invent panels in footage that has none.
- `sources`: graphic objects that the graphics exporter is responsible for, grouped by scene. Each object has a unique `id` within that scene and an `owner` that is one of its panels or `shared`. This universe excludes native text, panel fills, the scene background and preserved character-animation clips. It must come from the source scene/object map before export; a hand-written ownership claim is not visual proof.
- `segments`: exact native `id`, nonempty `scene`, `role` and `owner` for every draft segment. Optional `motionIntent.visibilityMethod` documents the actual visibility implementation; do not change that claim just to silence a diagnostic. Other project fields may be preserved without being interpreted.
- `fontDependencies`: for system fonts that cannot be redistributed, name the required font (for example `fontName:"Microsoft YaHei"`), record `redistributed:false` and the unresolved native resolution status. Empty paths do not prove a matching installed font. Packaged fonts still require permitted redistribution, portable paths and media hashes. Full native evidence currently requires file-bound fonts; a system-font dependency alone cannot satisfy that gate.

Roles and additional fields:

| Role | Owner | Requirements |
| --- | --- | --- |
| `background`, `animation` | panel ID or `shared` | Local video/image material on a video track. Preserved animation may be one finished clip. |
| `panel` | one panel ID | That panel's independently movable fill/frame material. |
| `graphics` | one panel ID | Nonempty `sourceObjectIds`; all belong to this panel. Use this role also for graphics that must be above text or a foreground panel. Keep layering in the native draft. |
| `shared_graphics` | `shared` | Nonempty `sourceObjectIds`; only genuine shared/cross-panel connectors, packets or objects. Do not use `shared` to hide an all-card bake. |
| `text`, `brand` | panel ID or `shared` | Native `texts` material on a text track; nonempty `textKey` unique within a scene and unique text material per segment. One segment per continuous appearance; necessary reappearances use unique occurrence keys plus a common optional `logicalTextKey` and edit-index relationship. |
| `narration`, `sfx`, `music` | panel ID or `shared` | Native audio material and audio track; `expectedVolume` is mandatory. |

`sourceObjectIds` is reserved for the two graphics roles. Each source object is assigned exactly once to one exported graphics segment in that scene. If the source truly uses multiple non-contiguous graphic exports, give those export units distinct source IDs with recorded common origin instead of duplicating one source ID. This convention allows exact coverage checks without confusing source identity and repeated display.

`expectedVolume` is the intended final **linear** native segment gain (1 means 0 dB). It is mandatory for all audio-track segments and video-track segments with nonzero audio, and may be supplied for silent video segments as 0. `audioGainBakedDb` optionally records preprocessing already applied to the media. The validator compares actual volume with `expectedVolume`; it never infers the right gain from the baked value. A voice media file already processed by −2.9 dB usually has `audioGainBakedDb:-2.9, expectedVolume:1`, unless an additional gain is explicitly intended and recorded. Media-level mix duplication, perceived loudness and sample alignment need a separate audio check.

Optional provenance may record `editorFamily`, editor/library versions and source commit, adapter hashes, font dependencies and capability decisions. These fields are not official draft fields or native proof. Do not fill them from another machine's assumptions.

## Native data checked

The validator expects the ordinary readable draft fields `materials`, `tracks`, `target_timerange`, `material_id`, `extra_material_refs`, `group_id`, `volume` and native material IDs. It is independent of a particular Python draft library. It rejects a package whose native structure does not match this supported contract; adapt a new native format deliberately instead of silently skipping checks.

Tracks may be reused across scenes. Intervals are half-open `[start,end)` with 1 µs rounding tolerance; actual overlapping segments within one track fail. Groups cannot link different `(scene,owner)` identities. Panel/graphics/native-text material IDs cannot be shared across owners or scenes; text segments cannot share text material IDs at all. Background and preserved animation may intentionally reuse materials. No particular number or naming order of tracks is required.

Native editable text, unique source ownership and unlinked groups do not by themselves prove visual independence. When the user requests the corresponding visual review, render or composite the actual encoded assets and move/hide/scale a panel's contents, checking that adjacent panels remain unchanged. Review transparent codec support, text appearance, occlusion and audio only within the requested scope. This script does not render video, inspect content pixels, open Jianying, inspect compound-clip internals or certify native editor playback/export.

The structure checker also covers ID uniqueness across native categories, finite keyframe values, ordered unique offsets within the segment, serialized scaling-mode conflicts, source audio bounds and fixed-speed relationships. Audio checks use declared metadata (`audioValidation:"metadata_only"`), not decoding or listening. Curved speed cannot be certified by a constant-speed equation.

Native text Alpha and zero-scale transitions receive explicit motion findings. An authored scale-to-zero animation is not automatically invalid. A declared `motionIntent.visibilityMethod` of `zero_scale`, `scale_zero` or `alpha_to_scale` combined with a zero-scale transition is rejected because the adapter is replacing visibility with geometry. Explicit `scalePurpose:"source_animation"` with `visibilityMethod` of `segment_ranges`, `native_animation` or `native_alpha` moves scale findings to informational `motionInfo`, marked `verification:"source_intent_declared_only"`; it does not certify native support. Actual text Alpha remains independently warned. Unknown intent and unverified text Alpha are warnings that require a scope-appropriate decision; do not relabel the intent to hide a defect. See [text-motion.md](text-motion.md).

## Running and results

Optional review commands, never automatic post-export steps:

```powershell
python scripts/validate_package.py --package "D:\project\jianying-package" --structure-only --report "D:\project\package-check.json"
python scripts/validate_package.py --package "D:\project\jianying-package" --require-native-evidence --report "D:\project\native-evidence-check.json"
```

Standard library only. Exit status is 0 for the requested checks passing, 1 for validation failure. Always inspect the separate readiness and warning fields rather than treating exit 0 as native approval. The same report is printed as UTF-8 JSON and optionally written to `--report`. Python callers use `validate_package(Path(...), structure_only=True)` or `require_native_evidence=True`. The legacy default still requires [native calibration and final-layout evidence](native-evidence.md); new callers should state their mode explicitly. `--native-evidence` selects another JSON inside the package. Missing or stale evidence fails the full evidence gate without undoing export completion.

Report fields include `status`, `passed`, `deliveryReady`, `validationMode`, `structuralValidation`, `motionValidation`, `warnings`, `motionInfo`, `fontValidation`, `fontWarnings`, `checks`, `errors`, package/draft hashes and `nativeValidation`. Structure mode returns `status:"structure_passed"`, `nativeValidation:"not_performed"` and `deliveryReady:false`. Evidence mode can verify recorded provenance, hashes and sample coverage; it never generates visual approval. Pending motion warnings keep `motionValidation:"requires_review"` and `deliveryReady:false` even when static layout evidence passes; information-only source-intent declarations do not. No warning is not a motion test: `motionValidation` remains `not_performed` if no dynamic review occurred. `deliveryReady` refers to this evidence gate, not whether export files exist or registration happened. Playback and full export remain separate checks.

`--allow-unvalidated-test-draft` remains a legacy test mode: successful status is `test_only_passed`, `deliveryReady:false`, and `nativeValidation:"bypassed_for_test_only"`. It is mutually exclusive with the two explicit modes. Use `--structure-only` for ordinary structure review; do not disguise an ordinary export as a test to bypass a native gate. Normal export-only work needs neither this flag nor this script.
