# Portable package contract (schemaVersion 1)

This is an interchange and validation contract for this skill, not Jianying's native schema. Adapt the current project's exporter into it; do not hard-code the historical episode. The package root contains `manifest.json`, `draft_content.json` and local media. Additional cover images, notes and source files are allowed. The installer rebases portable paths only after this package passes verification.

The default skill task builds this package, registers a new draft on the current computer, and delivers a portable ZIP with a double-click import entry. An explicit export-only request skips registration. The installer performs its necessary structural/media/index checks; the standalone review commands below still require a user review request. Missing native evidence does not prevent ordinary export or registration. Report export, portable archive, registration and review separately; review remains `not_performed` until requested and performed. Modifying this skill alone does not authorize importing an actual draft.

```json
{
  "schemaVersion": 1,
  "layeringMode": "card_text_split",
  "project": {"name": "Example", "width": 1920, "height": 1080, "fps": 30, "durationUs": 5000000},
  "media": [{"path": "media/card_visual.mp4", "bytes": 1234, "sha256": "<64 hex digits>"}],
  "panels": [{"scene": "C01", "id": "card_visual", "label": "Card non-text composite"}],
  "sources": [{"scene": "C01", "objects": [{"id": "background", "owner": "card_visual"}, {"id": "frame", "owner": "card_visual"}, {"id": "route", "owner": "card_visual"}]}],
  "segments": [
    {"id": "native-visual-id", "scene": "C01", "role": "graphics", "owner": "card_visual", "sourceObjectIds": ["background", "frame", "route"]},
    {"id": "native-title-id", "scene": "C01", "role": "text", "owner": "card_visual", "textKey": "title"}
  ]
}
```

This abbreviated example is not a complete runnable draft. Every native segment must have exactly one manifest entry, and every nonempty referenced local material path, including fonts nested in JSON text content, must be in `media`. A declared system-font dependency may leave file paths empty; it is not a bundled or verified font.

## Manifest fields

- `layeringMode`: record `card_text_split` for new default exports, or `panel_split` only when the user explicitly requests independently editable card panels. This field describes information-card structure; illustration footage, its editable overlay text and text plates are separate units in either card mode. This is adapter metadata within schemaVersion 1; the current structural validator does not interpret or enforce it. Missing metadata in an old package does not authorize rewriting its structure. The exporter must implement the chosen mode rather than merely add a label.
- `project`: nonempty `name`, positive integer `width`, `height`, `durationUs`; positive numeric `fps`. They must match the draft's `name`, `canvas_config`, `duration` and `fps`. Timeline units are integer microseconds; comparison permits 1 µs rounding at boundaries. Duration equals the greatest segment end; trailing intentional silence needs a corresponding timeline segment.
- `media`: each local media/font path, exact byte length and SHA-256. Paths are relative to the package root; no drive letters, URLs, parent traversal or symlink escape. `/` is preferred; `\` is accepted. Empty native optional path fields are ignored. Sidecar documentation not referenced as draft material need not be listed.
- `panels`: export-unit owners, uniquely identified by `(scene,id)`. In `card_text_split`, register one non-text unit per card, conventionally `id:"card_visual"`; the field name does not require drawing or splitting a physical panel. Different cards in one scene need distinct owner IDs. For illustration scenes, register the actual illustration, each editable text block and each independent text plate as distinct export units, as shown below; do not invent visual frames. In `panel_split`, card owners represent independent large boxes, including text-only boxes. IDs are stable and cannot be `shared`; labels are optional.
- `sources`: objects that the graphics exporter is responsible for, grouped by scene. Each object has a unique `id` within that scene and an `owner` in `panels` or `shared`. In `card_text_split`, include all of the card's non-text objects, including background, panel fills/frames, icons and cross-panel connections; assign all to the card's single export owner. Include independently extracted illustration text-plate objects when exported as `graphics`; exclude native text, separately handled narration captions/plates, audio and clean illustration media. In `panel_split`, exclude separately exported panel fills/background and assign graphics to their individual panel or `shared`. Derive the universe from the source scene/object map before export; ownership declarations are not visual proof.
- `segments`: exact native `id`, nonempty `scene`, `role` and `owner` for every draft segment. Optional `motionIntent.visibilityMethod` documents the actual visibility implementation; do not change that claim just to silence a diagnostic. Other project fields may be preserved without being interpreted.
- `fontDependencies`: for system fonts that cannot be redistributed, name the required font (for example `fontName:"Microsoft YaHei"`), record `redistributed:false` and the unresolved native resolution status. Empty paths do not prove a matching installed font. Packaged fonts still require permitted redistribution, portable paths and media hashes. Full native evidence currently requires file-bound fonts; a system-font dependency alone cannot satisfy that gate.

Roles and additional fields:

| Role | Owner | Requirements |
| --- | --- | --- |
| `background`, `animation` | export-unit ID or `shared` | Local video/image material on a video track. Each clean illustration/shot may be one image or clip, with exported text and its plate removed; separately handled narration caption plates may use `background` with a caption-purpose entry in the edit index. Default card backgrounds are inside that card's `graphics` composite, not an extra segment. |
| `panel` | one export-unit ID | Independently movable fill/frame in the optional `panel_split` mode; default card frames are inside `graphics`. |
| `graphics` | one export-unit ID | Nonempty `sourceObjectIds`, all belonging to this owner. For illustrations: each independent text plate is its own transparent graphic segment. For default cards: exactly one continuous non-text composite per card, including its background and all frames/connectors. Panel mode: per-panel graphics and any necessary foreground units. Preserve native ordering and resolve text occlusion without silently violating the selected mode. |
| `shared_graphics` | `shared` | Nonempty `sourceObjectIds`; genuine shared/cross-panel objects in `panel_split`. Default card connections belong inside the card's `graphics` composite. Do not label an all-card bake as shared or leave editable text baked into it. |
| `text`, `brand` | export-unit ID or `shared` | Native `texts` material on a text track; nonempty `textKey` unique within a scene and unique text material per segment. One segment per continuous appearance; necessary reappearances use unique occurrence keys plus a common optional `logicalTextKey` and edit-index relationship. |
| `narration`, `sfx`, `music` | export-unit ID or `shared` | Native audio material and audio track; `expectedVolume` is mandatory. |

`sourceObjectIds` is reserved for the two graphics roles. Each source object is assigned exactly once to one exported graphics segment in that scene. If the source truly uses multiple non-contiguous graphic exports, give those export units distinct source IDs with recorded common origin instead of duplicating one source ID. This convention allows exact coverage checks without confusing source identity and repeated display.

For the default mode, one card means one continuous card appearance; its internal motion states stay in the same composite clip. Do not split its background, frames or connections into additional visual segments, and do not merge successive cards into a single full-film clip. Keep narration captions and their bottom-centered plates separate. The existing validator checks source coverage and owner consistency, but does not enforce one composite per card or detect rasterized text in pixels. Those remain exporter obligations; visual review runs only on user request. A non-text foreground crossing editable text may make exact single-layer export impossible without supported native clipping/masking; surface that specific tradeoff instead of silently adding layers or flattening the text.

`expectedVolume` is the intended final **linear** native segment gain (1 means 0 dB). It is mandatory for all audio-track segments and video-track segments with nonzero audio, and may be supplied for silent video segments as 0. `audioGainBakedDb` optionally records preprocessing already applied to the media. The validator compares actual volume with `expectedVolume`; it never infers the right gain from the baked value. A voice media file already processed by −2.9 dB usually has `audioGainBakedDb:-2.9, expectedVolume:1`, unless an additional gain is explicitly intended and recorded. Media-level mix duplication, perceived loudness and sample alignment need a separate audio check.

Optional provenance may record `editorFamily`, editor/library versions and source commit, adapter hashes, font dependencies and capability decisions. These fields are not official draft fields or native proof. Do not fill them from another machine's assumptions.

## Illustration text and plate mapping

New exports keep each illustration/shot, each overlay text block and each independently authored text plate separate. This applies to illustration overlays, not scene paper textures or environmental backgrounds. It does not change the information-card composite rule. If there is no text or plate, omit that unit rather than add an empty track. Keep a text/plate pair spanning several illustrations continuous when that matches its actual appearance, and record the association in the edit index instead of splitting it at every image cut.

Example ownership mapping (abbreviated, not a complete native draft):

```json
{
  "schemaVersion": 1,
  "layeringMode": "card_text_split",
  "panels": [
    {"scene": "A01", "id": "illustration", "label": "Clean illustration"},
    {"scene": "A01", "id": "overlay_title", "label": "Editable illustration title"},
    {"scene": "A01", "id": "title_plate", "label": "Independent title plate"}
  ],
  "sources": [{"scene": "A01", "objects": [
    {"id": "title_fill", "owner": "title_plate"},
    {"id": "title_outline", "owner": "title_plate"}
  ]}],
  "segments": [
    {"id": "illustration_segment", "scene": "A01", "role": "animation", "owner": "illustration"},
    {"id": "plate_segment", "scene": "A01", "role": "graphics", "owner": "title_plate", "sourceObjectIds": ["title_fill", "title_outline"]},
    {"id": "title_segment", "scene": "A01", "role": "text", "owner": "overlay_title", "textKey": "title"}
  ]
}
```

The illustration and plate use separate native video/image materials and independently selectable segments; the title uses its own native `texts` material. Concurrent units need separate tracks with the original stacking, transforms and timing. Do not auto-group these units or place them inside an inseparable compound clip. Separate texture/frame objects already independently adjustable in the source remain separate plate units; fill/texture/outline of one authored plate may stay together. Only graphics roles use `sourceObjectIds`; provenance for the illustration and text belongs in the edit index.

Remove editable lettering from both the clean illustration and the plate media. A flattened image containing lettering/plates does not supply clean layers: obtain the editable source or a reliable clean export copy, and disclose missing inputs instead of duplicating the image on several tracks or covering old text with new text. Preserve the source files. Raster plates can be moved, scaled and replaced independently; internal colors, textures and paths require a source rerender unless actually represented by a supported independent native shape. The current structural validator can check these existing roles and owner/material relationships, but cannot detect baked text in pixels, guarantee a clean illustration or prove actual independent editing. User-requested review remains separate from export.

## Native data checked

The validator expects the ordinary readable draft fields `materials`, `tracks`, `target_timerange`, `material_id`, `extra_material_refs`, `group_id`, `volume` and native material IDs. It is independent of a particular Python draft library. It rejects a package whose native structure does not match this supported contract; adapt a new native format deliberately instead of silently skipping checks.

Tracks may be reused across scenes. Intervals are half-open `[start,end)` with 1 µs rounding tolerance; actual overlapping segments within one track fail. Groups cannot link different `(scene,owner)` identities. Panel/graphics/native-text material IDs cannot be shared across owners or scenes; text segments cannot share text material IDs at all. Background and preserved animation may intentionally reuse materials. No particular number or naming order of tracks is required.

Native editable text, unique source ownership and unlinked groups do not by themselves prove visual fidelity. For requested review of the default mode, inspect the actual encoded composite and native text for retained motion, complete non-text content, no duplicate raster text and correct occlusion. Internal frames intentionally move together as one card visual. Move/hide/scale independence between adjacent panels applies only to the optional `panel_split` mode and only when requested. Review transparent codec support, text appearance, occlusion and audio within the requested scope. This script does not render video, inspect content pixels, open Jianying, inspect compound-clip internals or certify native editor playback/export.

The structure checker also covers ID uniqueness across native categories, finite keyframe values, ordered unique offsets within the segment, serialized scaling-mode conflicts, source audio bounds and fixed-speed relationships. Audio checks use declared metadata (`audioValidation:"metadata_only"`), not decoding or listening. Curved speed cannot be certified by a constant-speed equation.

Native text Alpha and zero-scale transitions receive explicit motion findings. An authored scale-to-zero animation is not automatically invalid. A declared `motionIntent.visibilityMethod` of `zero_scale`, `scale_zero` or `alpha_to_scale` combined with a zero-scale transition is rejected because the adapter is replacing visibility with geometry. Explicit `scalePurpose:"source_animation"` with `visibilityMethod` of `segment_ranges`, `native_animation` or `native_alpha` moves scale findings to informational `motionInfo`, marked `verification:"source_intent_declared_only"`; it does not certify native support. Actual text Alpha remains independently warned. Unknown intent and unverified text Alpha are warnings that require a scope-appropriate decision; do not relabel the intent to hide a defect. See [text-motion.md](text-motion.md).

## Running and results

Optional review commands, never automatic post-export steps:

```powershell
python scripts/validate_package.py --package "D:\project\jianying-package" --structure-only --report "D:\project\package-check.json"
python scripts/validate_package.py --package "D:\project\jianying-package" --require-native-evidence --report "D:\project\native-evidence-check.json"
```

Standard library only. Exit status is 0 for the requested checks passing, 1 for validation failure. Always inspect the separate readiness and warning fields rather than treating exit 0 as native approval. The same report is printed as UTF-8 JSON and optionally written to `--report`. Calling without a mode now performs structure-only checks; Python callers can also state `validate_package(Path(...), structure_only=True)`. Existing callers that need [native calibration and final-layout evidence](native-evidence.md) must opt in with `require_native_evidence=True` or `--require-native-evidence`. `--native-evidence` selects another JSON inside the package and does not enable the gate by itself. Missing or stale evidence fails the explicit evidence gate without undoing export completion.

Report fields include `status`, `passed`, `deliveryReady`, `validationMode`, `structuralValidation`, `motionValidation`, `warnings`, `motionInfo`, `fontValidation`, `fontWarnings`, `checks`, `errors`, package/draft hashes and `nativeValidation`. Structure mode returns `status:"structure_passed"`, `nativeValidation:"not_performed"` and `deliveryReady:false`. Evidence mode can verify recorded provenance, hashes and sample coverage; it never generates visual approval. Pending motion warnings keep `motionValidation:"requires_review"` and `deliveryReady:false` even when static layout evidence passes; information-only source-intent declarations do not. No warning is not a motion test: `motionValidation` remains `not_performed` if no dynamic review occurred. `deliveryReady` refers to this evidence gate, not whether export files exist or registration happened. Playback and full export remain separate checks.

`--allow-unvalidated-test-draft` remains a legacy test mode: successful status is `test_only_passed`, `deliveryReady:false`, and `nativeValidation:"bypassed_for_test_only"`. It is mutually exclusive with the two explicit modes. Use `--structure-only` for ordinary structure review; do not disguise an ordinary export as a test to bypass a native gate. Normal export-only work needs neither this flag nor this script.
