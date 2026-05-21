"""
Revision API endpoint — apply JSON-Patch operations to mission narratives.

JSON-Patch (RFC 6902) lets callers express surgical edits:
  [{"op": "replace", "path": "/tone/primary", "value": "tense"}]

Validation is run BEFORE and AFTER the patch to prevent corrupt state.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import jsonpatch
import jsonschema
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()

# ---------------------------------------------------------------------------
# Narrative JSON schema (inline — loaded from file in production)
# ---------------------------------------------------------------------------

NARRATIVE_SCHEMA: dict = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["title", "factions", "biome", "tone", "pacing"],
    "properties": {
        "title": {"type": "string", "minLength": 1},
        "tagline": {"type": "string"},
        "premise": {"type": "string"},
        "factions": {
            "type": "object",
            "required": ["player", "ai"],
            "properties": {
                "player": {"type": "object", "required": ["id"]},
                "ai": {"type": "object", "required": ["id"]},
            },
        },
        "biome": {
            "type": "object",
            "required": ["map_id_ref"],
            "properties": {
                "map_id_ref": {"type": "string"},
                "region_hint": {"type": "string"},
            },
        },
        "tone": {
            "type": "object",
            "required": ["primary"],
            "properties": {
                "primary": {"type": "string"},
                "secondary": {"type": "array", "items": {"type": "string"}},
            },
        },
        "pacing": {"type": "object"},
    },
    "additionalProperties": True,
}


# ---------------------------------------------------------------------------
# Pydantic request / response models
# ---------------------------------------------------------------------------

class PatchOperation(BaseModel):
    op: str = Field(..., description="JSON-Patch operation: add | remove | replace | move | copy | test")
    path: str = Field(..., description="JSON Pointer (e.g. '/tone/primary')")
    value: Any | None = Field(None, description="New value (required for add/replace)")
    from_: str | None = Field(None, alias="from", description="Source path (for move/copy)")

    model_config = {"populate_by_name": True}


class RevisionRequest(BaseModel):
    mission_id: str = Field(..., description="Mission identifier (e.g. 'night-recon-everon')")
    patch: list[PatchOperation] = Field(..., min_length=1, description="JSON-Patch operations")
    description: str = Field("", description="Human-readable summary of this revision")


class RevisionResult(BaseModel):
    mission_id: str
    description: str
    operations_applied: int
    before_sha: str
    after_sha: str
    patched_narrative: dict


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _validate_narrative(data: dict) -> None:
    """Raise HTTPException(422) if narrative violates schema."""
    try:
        jsonschema.validate(data, NARRATIVE_SCHEMA)
    except jsonschema.ValidationError as exc:
        raise HTTPException(status_code=422, detail=f"Schema validation failed: {exc.message}")


def _sha_short(data: dict) -> str:
    import hashlib
    blob = json.dumps(data, sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()[:12]


def _mission_narrative_path(repo_root: Path, mission_id: str) -> Path:
    """Resolve the narrative.json for a mission."""
    return repo_root / "missions" / mission_id / "narrative.json"


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parents[2]  # backend/routes/ → repo root


@router.post("/revise", response_model=RevisionResult)
async def revise_mission(request: RevisionRequest) -> RevisionResult:
    """
    Apply JSON-Patch to a mission's narrative.json.

    Steps:
    1. Load narrative.json for mission_id
    2. Validate against schema (pre-check)
    3. Apply patch operations
    4. Validate against schema (post-check)
    5. Write updated narrative.json to disk
    6. Return diff summary
    """
    narrative_path = _mission_narrative_path(REPO_ROOT, request.mission_id)

    if not narrative_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Narrative not found: {narrative_path.relative_to(REPO_ROOT)}"
        )

    # Load
    before: dict = json.loads(narrative_path.read_text(encoding="utf-8"))
    _validate_narrative(before)
    before_sha = _sha_short(before)

    # Build patch
    patch_ops = [
        {k: v for k, v in op.model_dump(by_alias=True).items() if v is not None}
        for op in request.patch
    ]
    patch = jsonpatch.JsonPatch(patch_ops)

    # Apply
    try:
        after: dict = patch.apply(copy.deepcopy(before))
    except (jsonpatch.JsonPatchException, jsonpatch.JsonPointerException) as exc:
        raise HTTPException(status_code=422, detail=f"Patch failed: {exc}")

    # Post-validate
    _validate_narrative(after)
    after_sha = _sha_short(after)

    # Write (only if something changed)
    if before_sha != after_sha:
        narrative_path.write_text(
            json.dumps(after, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    return RevisionResult(
        mission_id=request.mission_id,
        description=request.description,
        operations_applied=len(patch_ops),
        before_sha=before_sha,
        after_sha=after_sha,
        patched_narrative=after,
    )
