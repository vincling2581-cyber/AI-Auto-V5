"""Check a new episode's declared card design before rendering.

This checks references and declarations only. It cannot prove that a recipe was
implemented, an override was authorized, or any rendered process is meaningful.
Encoded output observations may remain not_performed before rendering.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def strings(value, allow_empty=False):
    return (isinstance(value, list) and (allow_empty or bool(value))
            and all(nonempty(item) for item in value))


def contained(root, relative):
    if not nonempty(relative):
        raise ValueError("Missing episode-relative file path")
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError("Path leaves episode root: " + relative)
    return path


def validate(episode_root, contract_path=None, effective_defaults_path=None,
             locked_defaults_path=None):
    root = Path(episode_root).resolve()
    errors = []
    report = {
        "passed": False, "status": "failed", "errors": errors, "count": 0,
        "information_card_clip_count": 0,
        "scope": "declared_card_selection_implementation_references_and_palette_only",
        "actual_renderer_parameter_consumption": "not_proven",
        "pixel_and_semantic_review": "not_performed",
        "normal_speed_subjective_av": "not_performed",
        "override_authorization": "declaration_only_not_independently_verified",
    }

    def check(condition, message):
        if not condition:
            errors.append(message)

    try:
        contract = read_json(contract_path or root / "03_storyboard/production_contract.json")
        clips = contract["clips"]
        if not isinstance(clips, list) or any(not isinstance(clip, dict) for clip in clips):
            raise ValueError("Production contract clips must be an array of objects")
        card_clips = [clip for clip in clips if clip.get("layer") == "information_card"]
        report["information_card_clip_count"] = len(card_clips)
        if not card_clips:
            report.update(passed=True, status="not_applicable")
            return report
        expected_ids = [clip.get("id") for clip in card_clips]
        if not strings(expected_ids) or len(expected_ids) != len(set(expected_ids)):
            raise ValueError("Information-card clip IDs must be nonempty and unique")

        state = read_json(root / "00_brief/episode_state.json")
        design_path = contained(root, state["authoritative_files"]["semantic_design"])
        design = read_json(design_path)
        report["semantic_design"] = str(design_path)
        report["semantic_design_sha256"] = hashlib.sha256(design_path.read_bytes()).hexdigest()
        if not isinstance(design, dict):
            raise ValueError("Semantic design must be an object")
        check(design.get("is_template") is False,
              "Semantic design must explicitly set is_template=false after completion")
        library = design.get("library")
        if not isinstance(library, dict):
            raise ValueError("Missing semantic design library declaration")
        check(nonempty(library.get("source_commit")), "Missing library.source_commit")
        catalog_hash = library.get("catalog_sha256")
        check(isinstance(catalog_hash, str) and re.fullmatch(r"[0-9a-fA-F]{64}", catalog_hash) is not None,
              "library.catalog_sha256 must be a SHA-256 declaration")

        effective = read_json(effective_defaults_path or root / "00_brief/effective_defaults.json")["cards"]
        locked = read_json(locked_defaults_path or Path(__file__).with_name("defaults.json"))["cards"]
        theme, palette = effective.get("default_theme"), effective.get("palette")
        presets = effective.get("palette_presets")
        if not nonempty(theme) or not isinstance(palette, dict) or not palette or not isinstance(presets, dict):
            raise ValueError("Effective cards theme, palette and palette_presets must be populated")
        check(theme in presets and palette == presets.get(theme),
              "Effective cards.palette must equal cards.palette_presets[cards.default_theme]")
        overrides = state.get("scoped_overrides", [])
        if not isinstance(overrides, list):
            raise ValueError("episode_state.scoped_overrides must be an array")
        has_override = any(
            isinstance(item, dict) and item.get("scope") == "information_cards"
            and item.get("field") == "cards.palette" and nonempty(item.get("reason"))
            and nonempty(item.get("user_basis")) for item in overrides)
        report["palette_override_declared"] = has_override
        if not has_override:
            check(theme == locked.get("default_theme") and palette == locked.get("palette"),
                  "Effective cards palette/theme differs from locked defaults without an explicit information_cards palette override")

        cards = design.get("cards")
        if not isinstance(cards, list):
            raise ValueError("Semantic design cards must be an array")
        report["count"] = len(cards)
        card_ids, covered = [], []
        for index, card in enumerate(cards):
            label = f"Card {index + 1}"
            if not isinstance(card, dict):
                errors.append(label + " must be an object")
                continue
            cid = card.get("card_id")
            check(nonempty(cid), label + " missing card_id")
            if nonempty(cid):
                card_ids.append(cid)
                label += " (" + cid + ")"
            clip_ids = card.get("clip_ids")
            check(strings(clip_ids), label + " needs nonempty clip_ids")
            if strings(clip_ids):
                covered.extend(clip_ids)
            check(nonempty(card.get("relation")), label + " missing relation")
            selection = card.get("motion_selection")
            if not isinstance(selection, dict):
                errors.append(label + " missing motion_selection")
            else:
                for field in ("queries", "candidates_read"):
                    check(strings(selection.get(field)), label + " needs nonempty motion_selection." + field)
                recipe_ids = selection.get("recipe_ids")
                check(strings(recipe_ids, allow_empty=True), label + " recipe_ids must be an array of nonempty IDs or []")
                check(nonempty(selection.get("reason")), label + " missing selection reason")
                if recipe_ids == []:
                    check(nonempty(selection.get("custom_reason")), label + " needs custom_reason when no recipe is selected")
                process = selection.get("expected_process")
                for field in ("initial", "transition", "result"):
                    check(isinstance(process, dict) and nonempty(process.get(field)),
                          label + " missing expected_process." + field)
                anchors = selection.get("narration_anchors")
                check(isinstance(anchors, list) and bool(anchors)
                      and all(isinstance(anchor, dict) and bool(anchor) for anchor in anchors),
                      label + " narration_anchors must contain nonempty records")
            implementation = card.get("implementation")
            if not isinstance(implementation, dict):
                errors.append(label + " missing implementation")
            else:
                check(nonempty(implementation.get("symbol")), label + " missing implementation.symbol")
                try:
                    source = contained(root, implementation.get("path"))
                    check(source.is_file(), label + " implementation source does not exist: " + str(source))
                except ValueError as exc:
                    errors.append(label + " implementation: " + str(exc))
            card_palette = card.get("palette")
            card_theme = card_palette.get("theme") if isinstance(card_palette, dict) else None
            check(nonempty(card_theme), label + " missing palette.theme")
            if nonempty(card_theme):
                check(card_theme in presets, label + " palette.theme is not a registered preset")
                check(card_theme == theme, label + " palette.theme must match the episode default_theme, including with a palette override")

        for cid, count in Counter(card_ids).items():
            check(count == 1, "Duplicate card_id: " + cid)
        coverage = Counter(covered)
        for clip_id in expected_ids:
            check(coverage[clip_id] == 1,
                  f"Information-card clip {clip_id} must be covered exactly once; found {coverage[clip_id]}")
        for clip_id in sorted(set(covered) - set(expected_ids)):
            errors.append("Design references a non-information-card or unknown clip: " + clip_id)
        report.update(passed=not errors, status="passed" if not errors else "failed")
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        errors.append(str(exc))
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--episode-root", type=Path, required=True)
    args = parser.parse_args(argv)
    result = validate(args.episode_root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
