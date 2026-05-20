"""GUID Minter — generates new mission-unique GUIDs.

Arma Reforger uses 16-character uppercase hex GUIDs.
Observed pattern suggests timestamp + random suffix, but the engine
only requires uniqueness within the addon tree (not cryptographic).

Strategy: random 16 uppercase hex, deduplicated against catalog and local mint log.
Minted GUIDs are tracked in missions/{id}/mint-log.json to prevent collision.
"""
import os
import json
import secrets
from pathlib import Path


def mint_guid() -> str:
    """Mint a new random 16-char uppercase hex GUID."""
    return secrets.token_hex(8).upper()


def mint_unique_guid(
    catalog_index: dict,
    mission_dir: Path | None = None,
    max_attempts: int = 100,
) -> str:
    """Mint a GUID that doesn't collide with catalog or local mint log.

    Args:
        catalog_index: loaded INDEX.json dict
        mission_dir: if provided, tracks minted GUIDs in mint-log.json
        max_attempts: safety ceiling

    Returns:
        16-char uppercase hex string

    Raises:
        RuntimeError: if unable to mint unique GUID in max_attempts
    """
    existing_guids: set[str] = set(catalog_index.get("guid_to_type", {}).keys())

    # Load local mint log if available
    mint_log: list[str] = []
    mint_log_path: Path | None = None
    if mission_dir:
        mint_log_path = mission_dir / "mint-log.json"
        if mint_log_path.exists():
            mint_log = json.loads(mint_log_path.read_text())
        existing_guids.update(mint_log)

    for _ in range(max_attempts):
        guid = mint_guid()
        if guid not in existing_guids:
            # Record it
            existing_guids.add(guid)
            if mint_log_path is not None:
                mint_log.append(guid)
                mint_log_path.write_text(json.dumps(mint_log, indent=2))
            return guid

    raise RuntimeError(f"Failed to mint unique GUID after {max_attempts} attempts")


def mint_mission_guids(
    catalog_index: dict,
    mission_dir: Path,
) -> dict[str, str]:
    """Mint all GUIDs needed for a new mission addon tree.

    GUIDs are STABLE across re-runs: on first call they are minted and written
    to mint-log.json as a keyed dict. On subsequent calls the same GUIDs are
    returned from the log without re-minting.

    Returns dict with keys:
      addon_guid, mission_header_guid, world_guid
    """
    GUID_KEYS = ("addon_guid", "mission_header_guid", "world_guid")
    mint_log_path = mission_dir / "mint-log.json"

    # Load existing keyed log if present
    existing: dict = {}
    if mint_log_path.exists():
        try:
            raw = json.loads(mint_log_path.read_text())
            if isinstance(raw, dict):
                existing = raw
            elif isinstance(raw, list):
                # Migrate legacy flat list format: cannot recover keys — will re-mint
                existing = {"_legacy_guids": raw}
        except (json.JSONDecodeError, OSError):
            existing = {}

    # Return cached keys if all present
    if all(k in existing for k in GUID_KEYS):
        return {k: existing[k] for k in GUID_KEYS}

    # Mint any missing keys
    known_guids: set[str] = set(catalog_index.get("guid_to_type", {}).keys())
    # Include any already-minted GUIDs to prevent collision
    for k, v in existing.items():
        if isinstance(v, str) and len(v) == 16:
            known_guids.add(v)

    result: dict[str, str] = {}
    for k in GUID_KEYS:
        if k in existing and len(existing[k]) == 16:
            result[k] = existing[k]
        else:
            # Mint fresh, deduplicating against all known + already-minted
            for _ in range(100):
                g = mint_guid()
                if g not in known_guids:
                    known_guids.add(g)
                    result[k] = g
                    break
            else:
                raise RuntimeError(f"Unable to mint unique GUID for key '{k}'")

    # Persist the keyed log (merge with existing so legacy_guids are preserved)
    existing.update(result)
    mint_log_path.write_text(json.dumps(existing, indent=2))
    return result


def mint_log_list(mission_dir: Path) -> list[str]:
    """Return all minted GUIDs for this mission as a flat list (for validator)."""
    mint_log_path = mission_dir / "mint-log.json"
    if not mint_log_path.exists():
        return []
    try:
        raw = json.loads(mint_log_path.read_text())
        if isinstance(raw, list):
            return [g for g in raw if isinstance(g, str) and len(g) == 16]
        if isinstance(raw, dict):
            return [v for v in raw.values() if isinstance(v, str) and len(v) == 16]
    except (json.JSONDecodeError, OSError):
        return []
    return []
