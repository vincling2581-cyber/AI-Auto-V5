"""Read-only integrity/configuration check for the V5 static-comic standard.

No rendering, episode creation, editor operations, or media review.
Use --project-root only when checking the active project pointer as well.
"""
from pathlib import Path
import argparse
import hashlib
import json

STANDARD_ROOT = Path(__file__).resolve().parent.parent


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_path(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Path escapes standard/project root: " + relative)
    return path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify(root=STANDARD_ROOT, project_root=None):
    root = root.resolve()
    manifest_path = root / "production_standard.json"
    manifest = read_json(manifest_path)
    require(manifest["version"] == "4.7", "Expected v4.7")
    require(manifest["status"] == "active", "Standard is not active")
    require(manifest["approval"]["mode"] == "explicit_user_confirmation", "Missing current user authorization")
    require(bool(manifest["approval"]["authorized_quote"]), "Missing authorization text")
    files = manifest["files"]
    paths = [item["path"] for item in files]
    require(len(paths) == len(set(paths)), "Duplicate manifest path")
    for key in ("sop", "prompts", "prompts_data", "defaults", "rules", "rules_readable", "changes", "visual_references", "brand_assets", "verifier", "layer_contract", "episode_validator", "episode_contract_template"):
        require(manifest[key] in paths, "Untracked required file: " + key)
    for item in files:
        path = local_path(root, item["path"])
        require(path.is_file(), "Missing standard file: " + item["path"])
        require(sha256(path) == item["sha256"], "Hash mismatch: " + item["path"])
        if path.suffix == ".json":
            read_json(path)
    lock = root / "standard_lock.json"
    require(lock.read_bytes() == manifest_path.read_bytes(), "Standard lock differs from manifest")

    defaults = read_json(local_path(root, manifest["defaults"]))
    require(defaults["version"] == manifest["version"], "Defaults version mismatch")
    animation = defaults["animation"]
    require(animation["timing_policy"] == "semantic_sequence_with_still_cap", "Timing policy must use semantic sequences and a still-image cap")
    require(animation["max_static_seconds"] == 2.0, "Illustration cap must be 2.0 seconds")
    for field in ("target_static_seconds", "fixed_cut_interval_seconds", "minimum_state_seconds", "fixed_action_shot_ratio", "frame_count_quota"):
        require(animation[field] is None, "Unexpected time/quota constraint: " + field)
    require(animation["split_complete_meaning_to_meet_timer"] is False, "Mechanical splitting enabled")
    require(animation["continuous_hold_across_srt_allowed"] is True, "Semantic cross-SRT hold disabled")
    illustration = defaults["illustration"]
    require(illustration["semantic_relation_alone_allows_hold"] is False, "Topic relation alone cannot justify a scene hold")
    require(illustration["scene_group_requires_narrative_progress"] is True, "Missing scene-group narrative progress")
    require(illustration["fixed_scene_duration_seconds"] is None, "Unexpected scene-duration quota")
    require(illustration["scene_contract_fields"] == ["scene_id", "scene_progress"], "Scene contract fields mismatch")
    require(illustration["scene_change_reason_required_on_scene_change"] is True, "Missing scene change reason policy")
    require(illustration["presentation_mode"] == "static_comic_sequence", "Illustration mode must be static comic")
    require(illustration["transition"] == "hard_cut", "Illustration transitions must be hard cuts")
    require(illustration["internal_motion_allowed"] is False, "Illustration internal motion enabled")
    require(illustration["camera_motion_allowed"] is False and animation["camera_motion_allowed"] is False and animation["internal_motion_allowed"] is False, "Illustration camera/internal motion enabled")
    require(illustration["corner_labels_enabled"] is False and animation["corner_labels_enabled"] is False, "Illustration corner labels enabled")
    for field in ("default_setting", "fixed_outdoor_ratio", "fixed_scene_count", "fixed_illustration_share"):
        require(illustration[field] is None, "Unexpected illustration constraint: " + field)
    cards = defaults["cards"]
    require(cards["max_static_seconds"] is None, "Illustration cap must not constrain information cards")
    require(cards["corner_labels_enabled"] is False, "Card corner labels enabled")
    require(cards["layout_policy"] == "semantic_relation_before_container", "Layout must follow semantic relation")
    require(cards["container_required"] is False and cards["default_layout"] is None, "Forced card container/layout")
    require(cards["fixed_card_share"] is None and cards["fixed_layout_count"] is None, "Unexpected card quota")
    require(cards["reading_hold_allowed"] and cards["render_continuous_intermediate_frames"], "Missing process/reading requirement")
    require({"paper", "dark"}.issubset(cards["palette_presets"]), "Missing palette choices")
    require(cards["palette"] == cards["palette_presets"][cards["default_theme"]], "Default palette/theme mismatch")
    for palette in cards["palette_presets"].values():
        require(palette["background"] != palette["text"], "Background and text are identical")
    require(defaults["layout"]["reserved_bottom_band_px"] == 0, "Blank lower band introduced")
    require(defaults["layout"]["corner_labels_enabled"] is False and defaults["layout"]["badge_optional"] is False, "Fixed corner labels must be off")
    require(defaults["layout"]["subtitle_independent_layer"] is True and defaults["layout"]["subtitle_alignment"] == "bottom_center", "Spoken caption defaults mismatch")
    require(defaults["audio"]["preserve_provided_voice"] is True, "Voice preservation changed")
    require(defaults["delivery"]["jianying_import_default"] is False, "Unrequested Jianying default")
    contract = read_json(local_path(root, manifest["layer_contract"]))
    require(contract["standard_version"] == manifest["version"], "Layer contract version mismatch")
    require(contract["illustration"]["max_contiguous_image_seconds"] == 2.0, "Layer contract cap mismatch")
    require(contract["illustration"]["motion"] == "none" and contract["illustration"]["transition"] == "hard_cut", "Layer contract stillness mismatch")
    require(contract["illustration"]["required_scene_fields"] == illustration["scene_contract_fields"], "Contract/defaults scene field mismatch")
    require(contract["illustration"]["planning_levels"] == illustration["planning_levels"], "Scene planning vocabulary mismatch")
    require(contract["information_card"]["static_purpose_field"] == "static_card_purpose", "Missing explicit static-card exemption")
    require(contract["information_card"]["max_contiguous_image_seconds"] is None, "Card cap introduced in layer contract")
    require(all(contract[key]["corner_labels"] is False for key in ("illustration", "information_card")), "Layer contract corner labels enabled")
    template = read_json(local_path(root, manifest["episode_contract_template"]))
    require(template["is_template"] is True and template["standard_version"] == manifest["version"], "Episode contract template mismatch")
    require(defaults["layer_contract"]["schema"] == manifest["layer_contract"], "Defaults layer contract path mismatch")
    require(defaults["layer_contract"]["validator"] == manifest["episode_validator"], "Defaults validator path mismatch")

    prompts = read_json(local_path(root, manifest["prompts_data"]))
    rules = read_json(local_path(root, manifest["rules"]))
    require([p["id"] for p in prompts] == [f"P{i:02d}" for i in range(1, 15)], "Stage prompt IDs changed")
    for collection in (prompts, rules):
        ids = [item["id"] for item in collection]
        require(len(ids) == len(set(ids)), "Duplicate rule/prompt ID")
    for collection, field, document in ((prompts, "text", manifest["prompts"]), (rules, "rule", manifest["rules_readable"])):
        body = local_path(root, document).read_text(encoding="utf-8-sig")
        for item in collection:
            require(item[field] in body, "Readable document differs from JSON: " + item["id"])
    references = read_json(local_path(root, manifest["visual_references"]))
    require(references["standard_version"] == manifest["version"], "Visual reference version mismatch")
    method_root = cards["method_assets"]
    for relative in ("card_kit.js", "README.md", "vendor/flubber.min.js", "vendor/flubber-LICENSE", "vendor/THIRD_PARTY.md"):
        dependency = local_path(root, method_root + "/" + relative)
        require(dependency.relative_to(root).as_posix() in paths and dependency.is_file(), "Untracked or missing method dependency: " + str(dependency))
    assets = read_json(local_path(root, manifest["brand_assets"]))
    asset_paths = {asset["copy"] for asset in assets}
    for field in ("identity", "eye_reference"):
        require(defaults["brand_assets"][field] in asset_paths, "Unregistered brand dependency: " + field)
    for relative in (illustration["reference_manifest"], defaults["brand_assets"]["action_and_lower_edge_references"]):
        require(relative in paths and local_path(root, relative).is_file(), "Untracked visual reference manifest")
    for asset in assets:
        path = local_path(root, asset["copy"])
        require(asset["copy"] in paths and sha256(path) == asset["sha256"], "Brand reference mismatch")

    if project_root is not None:
        project_root = project_root.resolve()
        entry = read_json(project_root / "CURRENT_PROJECT.json")["standard"]
        require(entry["version"] == manifest["version"], "Project version mismatch")
        require(entry["revision"] == manifest["revision"], "Project revision mismatch")
        require(local_path(project_root, entry["snapshot_root"]) == root, "Project standard root mismatch")
        for field, expected in (("entry_point", manifest_path), ("lock", lock)):
            require(local_path(project_root, entry[field]) == expected, "Project pointer mismatch: " + field)
        require(entry["entry_sha256"] == sha256(manifest_path), "Project manifest hash mismatch")
        require(entry["lock_sha256"] == sha256(lock), "Project lock hash mismatch")
    return {"version": manifest["version"], "status": "passed", "files": len(files), "rules": len(rules), "prompts": len(prompts), "scope": "standard_integrity_and_configuration_only", "video_review": "not_performed"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(project_root=args.project_root), ensure_ascii=False, indent=2))
