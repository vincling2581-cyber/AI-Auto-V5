# Portable package contract (schemaVersion 1)

This is an interchange and validation contract for this skill, not Jianying's native schema. Adapt the current project's exporter into it; do not hard-code the historical episode. The package root contains `manifest.json`, `draft_content.json` and local media. Additional cover images, notes and source files are allowed. The installer rebases portable paths only after this package passes verification.

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

This abbreviated example is not a complete runnable draft. Every native segment must have exactly one manifest entry, and every referenced material path, including fonts nested in JSON text content, must be in `media`.

## Manifest fields

- `project`: nonempty `name`, positive integer `width`, `height`, `durationUs`; positive numeric `fps`. They must match the draft's `name`, `canvas_config`, `duration` and `fps`. Timeline units are integer microseconds; comparison permits 1 µs rounding at boundaries. Duration equals the greatest segment end; trailing intentional silence needs a corresponding timeline segment.
- `media`: each local media/font path, exact byte length and SHA-256. Paths are relative to the package root; no drive letters, URLs, parent traversal or symlink escape. `/` is preferred; `\` is accepted. Empty native optional path fields are ignored. Sidecar documentation not referenced as draft material need not be listed.
- `panels`: independent large-box owners, uniquely identified by `(scene,id)`. IDs are stable semantic IDs and cannot be `shared`; labels are optional. Panels with text only are valid. The manifest is a description of ownership, not a request to invent panels in footage that has none.
- `sources`: graphic objects that the graphics exporter is responsible for, grouped by scene. Each object has a unique `id` within that scene and an `owner` that is one of its panels or `shared`. This universe excludes native text, panel fills, the scene background and preserved character-animation clips. It must come from the source scene/object map before export; a hand-written ownership claim is not visual proof.
- `segments`: exact native `id`, nonempty `scene`, `role` and `owner` for every draft segment. Additional project fields are allowed and ignored by this validator.

Roles and additional fields:

| Role | Owner | Requirements |
| --- | --- | --- |
| `background`, `animation` | panel ID or `shared` | Local video/image material on a video track. Preserved animation may be one finished clip. |
| `panel` | one panel ID | That panel's independently movable fill/frame material. |
| `graphics` | one panel ID | Nonempty `sourceObjectIds`; all belong to this panel. Use this role also for graphics that must be above text or a foreground panel. Keep layering in the native draft. |
| `shared_graphics` | `shared` | Nonempty `sourceObjectIds`; only genuine shared/cross-panel connectors, packets or objects. Do not use `shared` to hide an all-card bake. |
| `text`, `brand` | panel ID or `shared` | Native `texts` material on a text track; nonempty `textKey` unique within a scene. One continuous segment per logical text; unique text material per segment. |
| `narration`, `sfx`, `music` | panel ID or `shared` | Native audio material and audio track; `expectedVolume` is mandatory. |

`sourceObjectIds` is reserved for the two graphics roles. Each source object is assigned exactly once to one exported graphics segment in that scene. If the source truly uses multiple non-contiguous graphic exports, give those export units distinct source IDs with recorded common origin instead of duplicating one source ID. This convention allows exact coverage checks without confusing source identity and repeated display.

`expectedVolume` is the intended final **linear** native segment gain (1 means 0 dB). It is mandatory for all audio-track segments and video-track segments with nonzero audio, and may be supplied for silent video segments as 0. `audioGainBakedDb` optionally records preprocessing already applied to the media. The validator compares actual volume with `expectedVolume`; it never infers the right gain from the baked value. A voice media file already processed by −2.9 dB usually has `audioGainBakedDb:-2.9, expectedVolume:1`, unless an additional gain is explicitly intended and recorded. Media-level mix duplication, perceived loudness and sample alignment need a separate audio check.

## Native data checked

The validator expects the ordinary readable draft fields `materials`, `tracks`, `target_timerange`, `material_id`, `extra_material_refs`, `group_id`, `volume` and native material IDs. It is independent of a particular Python draft library. It rejects a package whose native structure does not match this supported contract; adapt a new native format deliberately instead of silently skipping checks.

Tracks may be reused across scenes. Intervals are half-open `[start,end)` with 1 µs rounding tolerance; actual overlapping segments within one track fail. Groups cannot link different `(scene,owner)` identities. Panel/graphics/native-text material IDs cannot be shared across owners or scenes; text segments cannot share text material IDs at all. Background and preserved animation may intentionally reuse materials. No particular number or naming order of tracks is required.

Native editable text, unique source ownership and unlinked groups do not by themselves prove visual independence. Separately render or composite the actual encoded assets and move/hide/scale a panel's contents, checking that adjacent panels remain unchanged. Confirm transparent codec support, text appearance, occlusion and audio in the applicable runtime. This script does not render video, inspect content pixels, open Jianying, inspect compound-clip internals or certify native editor playback/export.

## Running and results

```powershell
python scripts/validate_package.py --package "D:\project\jianying-package" --report "D:\project\package-check.json"
```

Standard library only. Exit status is 0 for success, 1 for validation failure. The same report is printed as UTF-8 JSON and optionally written to `--report`. Python callers can import `validate_package` and call `validate_package(Path(...))`.

Report fields: `status` (`passed` or `failed`), `passed` (boolean), `checks` (objects with `name`, `passed`, `detail`), `errors` (failure strings), `packageRoot`, `manifestSha256`, `draftSha256`, `nativeValidation:"not_performed"`, `visualValidation:"not_performed"`. Hashes are present once the corresponding readable JSON files have loaded. Do not promote these machine checks to perceptual or native-Jianying acceptance.
