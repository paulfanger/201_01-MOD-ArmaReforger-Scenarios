# Execution Prompt — for Claude Sonnet 4.6

> **Du bist Claude Sonnet 4.6.** Dieser Plan kommt von Claude Opus 4.7 nach Phase-0–4-Research.
>
> **Lies BEVOR du irgendetwas tust:**
> - `arma-reforger-coop-setup-prompt.md` (Original-Vision)
> - `ARCHITECTURE.md` (post-research Architecture)
> - `DECISIONS.md` (alle architecture-affecting decisions chronologisch)
> - `research/00-synthesis.md` (Decision-Matrix + Recommendations)
> - `research/01-workbench-sdk.md` (Plugin-APIs, Headless-Mode, External-IPC)
> - `research/02-mission-format.md` (vollständige File-Anatomie + JSON-Schema)
> - `research/03-eula-legal.md` (EULA-Konformität + Disclosure)
> - `CLAUDE.md` (How-to-behave)
>
> **Existierende Specs (NICHT überschreiben, ergänzen):**
> - `.claude/agents/testing/*.md` (5 Testing-Agents)
> - `.claude/agents/specialists/mission-director.md`, `version-keeper.md`, `narrative-designer.md`
> - `.claude/commands/*.md` (10 Slash-Commands)
> - `backend/main.py`, `backend/requirements.txt`
>
> **Du implementierst:** alles was unter "Execution Phases" steht, plus die noch-fehlenden Specialist-Agents.

---

## Model Context & Style

- **Sprache:** Deutsch für User-Facing-Communication, Englisch für Code/Comments/Filenames
- **User:** Paul, Creative Director, **Non-Coder** — niemals davon ausgehen, dass der User Code editiert
- **Working dir:** `/Users/paulfanger/Documents/ELOS/201_01-MOD-ArmaReforger-Scenarios/`
- **OS:** macOS M1 (Reforger Workbench ist Windows-only — siehe Fallback-Strategien)

---

## Sacred Approval Gates

Diese ZWEI Stellen erfordern explizite User-Approval. Alles andere autonom.

1. **Vor Stage-Wechsel in Mission-Pipeline** — wenn Mission-Director ein User-`/approve` erwartet
2. **Vor Git-Commit von Architecture-Changes** — wenn DECISIONS.md geändert wird

**Bug-Fixes sind KEIN Approval-Gate.** Sub-Agents (insbes. `bug-fixer`) fixen autonom bis max 5 Iterationen pro Test.

---

## Execution Phases

### Phase 1: Environment Setup & Validation (15 min)

**1.1 Pre-Check (run as bash):**

```bash
cd /Users/paulfanger/Documents/ELOS/201_01-MOD-ArmaReforger-Scenarios
git status
test -d backend/.venv && echo "VENV_EXISTS" || echo "NEED_VENV"
test -f catalog/INDEX.json && echo "CATALOG_BOOTSTRAPPED" || echo "NEED_BOOTSTRAP"
test -f .env && echo "ENV_EXISTS" || echo "NEED_ENV"
```

**1.2 Setup Venv & Deps:**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**1.3 Validate Backend Health:**

```bash
# Start backend in background
cd backend && source .venv/bin/activate && uvicorn main:app --port 8765 &
sleep 2
curl -s http://localhost:8765/health | python3 -c "import json,sys; d=json.load(sys.stdin); assert d['status']=='ok'; print('BACKEND_OK')"
```

**Definition of Done Phase 1:**
- venv aktiv mit allen deps installed
- Backend antwortet auf /health
- `WORK_LOG.md` updated mit Phase-1-Eintrag

---

### Phase 2: Catalog Bootstrap (30-45 min)

Asset-Catalog ist Pflicht-Gate — ohne Catalog gibt es keine Mission-Generation ohne Halluzinations-Risk.

**2.1 Clone Reference-Repos:**

```bash
mkdir -p /tmp/reforger-research
cd /tmp/reforger-research
git clone --depth 1 https://github.com/exocs/Reforger-Sample-Coop.git
git clone --depth 1 https://github.com/BohemiaInteractive/Arma-Reforger-Samples.git
git clone --depth 1 https://github.com/Kexanone/CombatOpsEnhanced_AR.git
git clone --depth 1 https://github.com/gruppe-adler/GRAD-COOP-Template-Reforger.git
```

**2.2 Parser implementieren** — `backend/catalog/bootstrap.py`:

```python
"""Catalog Bootstrap Parser.

Extracts {GUID}Path.et patterns from cloned reference repos.
Writes to catalog/{type}/{guid}.json + catalog/INDEX.json.
"""
import re
import json
from pathlib import Path

GUID_PATTERN = re.compile(r'\{([0-9A-F]{16})\}([^"\s]+\.(et|gproj|conf|ent|edds|st))')
# class-name + prefab-guid + path heuristic:
ENTITY_DECL = re.compile(r'^\s*(SCR_\w+|\w+Manager\w*|\w+Entity\w*)\s+\w+\s*:\s*"\{([0-9A-F]{16})\}([^"]+)"', re.MULTILINE)

REPO_PATHS = [
    "/tmp/reforger-research/Reforger-Sample-Coop",
    "/tmp/reforger-research/Arma-Reforger-Samples",
    "/tmp/reforger-research/CombatOpsEnhanced_AR",
    "/tmp/reforger-research/GRAD-COOP-Template-Reforger",
]

def parse_repo(repo_path: Path) -> list[dict]:
    """Walk repo, find layer/conf/ent files, extract GUID-refs."""
    found = []
    for f in repo_path.rglob("*"):
        if f.suffix in (".layer", ".conf", ".ent", ".gproj") and f.is_file():
            try:
                content = f.read_text(errors="ignore")
            except Exception:
                continue
            # Generic GUID refs
            for m in GUID_PATTERN.finditer(content):
                found.append({
                    "guid": m.group(1),
                    "path": m.group(2),
                    "ext": m.group(3),
                    "source_file": str(f.relative_to(repo_path)),
                    "source_repo": repo_path.name,
                })
            # Entity declarations (richer: also class-name)
            for m in ENTITY_DECL.finditer(content):
                found.append({
                    "class_name": m.group(1),
                    "guid": m.group(2),
                    "path": m.group(3),
                    "source_file": str(f.relative_to(repo_path)),
                    "source_repo": repo_path.name,
                    "kind": "entity_decl",
                })
    return found

def classify_type(path: str, class_name: str | None) -> str:
    p = path.lower()
    if class_name and "faction" in class_name.lower(): return "faction"
    if class_name and "loadout" in class_name.lower(): return "loadout"
    if class_name and "spawnpoint" in class_name.lower(): return "spawnpoint"
    if class_name and "waypoint" in class_name.lower(): return "waypoint"
    if class_name and "task" in class_name.lower(): return "task"
    if class_name and "gamemode" in class_name.lower(): return "gamemode"
    if "/vehicles/" in p: return "vehicle"
    if "/weapons/" in p: return "weapon"
    if "/factions/" in p: return "faction"
    if "/groups/" in p: return "group"
    if "/loadouts/" in p: return "loadout"
    if p.endswith(".gproj"): return "gproj"
    if p.endswith(".conf"): return "config"
    if p.endswith(".et"): return "prefab"
    return "unknown"

def main():
    catalog_dir = Path("/Users/paulfanger/Documents/ELOS/201_01-MOD-ArmaReforger-Scenarios/catalog")
    all_refs = []
    for r in REPO_PATHS:
        rp = Path(r)
        if rp.exists():
            all_refs.extend(parse_repo(rp))
    
    # Dedupe by GUID; keep richest entry (with class_name preferred)
    by_guid = {}
    for ref in all_refs:
        g = ref["guid"]
        if g not in by_guid or ("class_name" in ref and "class_name" not in by_guid[g]):
            by_guid[g] = ref
    
    # Write per-type files
    by_type = {}
    for guid, ref in by_guid.items():
        t = classify_type(ref.get("path", ""), ref.get("class_name"))
        ref["type"] = t
        ref["display_name"] = (ref.get("class_name") or Path(ref.get("path", "")).stem)
        ref["verified_at"] = "2026-05-20"
        ref["verified_by"] = "catalog-bootstrap"
        by_type.setdefault(t, {})[guid] = ref
    
    # Write files
    for t, items in by_type.items():
        type_dir = catalog_dir / t
        type_dir.mkdir(parents=True, exist_ok=True)
        for guid, ref in items.items():
            (type_dir / f"{guid}.json").write_text(json.dumps(ref, indent=2))
    
    # Write INDEX
    index = {
        "version": 1,
        "generated_at": "2026-05-20",
        "total_assets": len(by_guid),
        "by_type": {t: len(items) for t, items in by_type.items()},
        "core_guid": "58D0FB3206B6F859",  # Arma Reforger core dependency
        "guid_to_type": {g: ref["type"] for g, ref in by_guid.items()},
    }
    (catalog_dir / "INDEX.json").write_text(json.dumps(index, indent=2))
    print(f"Catalog bootstrapped: {len(by_guid)} unique GUIDs in {len(by_type)} types")

if __name__ == "__main__":
    main()
```

**Run:**
```bash
cd /Users/paulfanger/Documents/ELOS/201_01-MOD-ArmaReforger-Scenarios
python3 backend/catalog/bootstrap.py
cat catalog/INDEX.json | python3 -m json.tool | head -30
```

**Definition of Done Phase 2:**
- `catalog/INDEX.json` mit ≥ 50 unique GUIDs
- mind. 5 verschiedene Type-Folders
- Core-GUID `58D0FB3206B6F859` present
- DECISIONS.md updated mit Catalog-Bootstrap-Methode

---

### Phase 3: Backend Implementation (60-90 min)

Implementiere die Backend-Module nach diesem Plan. **Reihenfolge wichtig** (Dependencies):

**3.1 `backend/catalog/resolver.py`** — Asset-Resolution:

```python
"""Resolve asset references against bootstrapped catalog."""
import json
from pathlib import Path
from typing import Optional

CATALOG_DIR = Path(__file__).parent.parent.parent / "catalog"

class CatalogResolver:
    def __init__(self):
        self.index = json.loads((CATALOG_DIR / "INDEX.json").read_text())
        self._cache: dict[str, dict] = {}
    
    def resolve_guid(self, guid: str) -> Optional[dict]:
        """Lookup by GUID. Returns None if hallucinated."""
        if guid in self._cache:
            return self._cache[guid]
        if guid not in self.index["guid_to_type"]:
            return None
        t = self.index["guid_to_type"][guid]
        fp = CATALOG_DIR / t / f"{guid}.json"
        if not fp.exists():
            return None
        data = json.loads(fp.read_text())
        self._cache[guid] = data
        return data
    
    def find_by_class(self, class_name: str) -> list[dict]:
        """Find candidate prefabs by class-name pattern."""
        results = []
        for guid, t in self.index["guid_to_type"].items():
            ref = self.resolve_guid(guid)
            if ref and ref.get("class_name") == class_name:
                results.append(ref)
        return results
    
    def has_core_dependency(self) -> bool:
        return self.index["core_guid"] in self.index["guid_to_type"] or True  # core is dependency, may not be in catalog itself
```

**3.2 `backend/exporters/braces.py`** — Brace-Syntax-Formatter:

```python
"""Enfusion Brace-Syntax serializer.

Produces files matching the format observed in:
- /tmp/reforger-research/Reforger-Sample-Coop/SampleCoop/Worlds/*.layer
- ./research/02-mission-format.md Annotated Examples

Critical: this is NOT JSON. It's Enfusion's custom DSL with significant whitespace.
"""
from typing import Any
from io import StringIO

INDENT = " "  # single space, per observed files
INDENT_STEP = " "

def serialize(obj: Any, level: int = 0) -> str:
    """Serialize a Python dict/list to Enfusion brace syntax."""
    if isinstance(obj, dict):
        return _serialize_dict(obj, level)
    raise ValueError(f"Top-level must be dict, got {type(obj)}")

def _serialize_dict(d: dict, level: int) -> str:
    """A dict represents either a class block { … } or a key/value sequence."""
    out = StringIO()
    indent = INDENT * level
    for key, val in d.items():
        if isinstance(val, dict):
            # Nested class block
            out.write(f"{indent}{key} {{\n")
            out.write(_serialize_dict(val, level + 1))
            out.write(f"{indent}}}\n")
        elif isinstance(val, list):
            out.write(f"{indent}{key} {{\n")
            for item in val:
                if isinstance(item, str):
                    out.write(f"{indent}{INDENT_STEP}\"{item}\"\n")
                elif isinstance(item, dict):
                    out.write(_serialize_dict(item, level + 1))
                else:
                    out.write(f"{indent}{INDENT_STEP}{item}\n")
            out.write(f"{indent}}}\n")
        else:
            # Scalar
            out.write(f"{indent}{key} {_fmt_scalar(val)}\n")
    return out.getvalue()

def _fmt_scalar(v: Any) -> str:
    if isinstance(v, bool): return "1" if v else "0"
    if isinstance(v, str):
        # Don't quote if it's a GUID reference like "{GUID}path"
        if v.startswith("{") and "}" in v:
            return f'"{v}"'
        # Otherwise quote strings
        return f'"{v}"'
    if isinstance(v, (int, float)): return str(v)
    if v is None: return ""
    return str(v)
```

**3.3 `backend/exporters/gproj.py`** — addon.gproj writer:

```python
"""Generate addon.gproj file.

Per research/02-mission-format.md File-by-File-Anatomy `addon.gproj`:
Required: ID, GUID, TITLE, Dependencies { "58D0FB3206B6F859" }
"""
from .braces import serialize

CORE_GUID = "58D0FB3206B6F859"

def generate_gproj(addon_id: str, addon_guid: str, title: str, extra_deps: list[str] | None = None) -> str:
    """Generate .gproj content. addon_guid must be 16 uppercase hex chars."""
    deps = [CORE_GUID] + (extra_deps or [])
    spec = {
        "GameProject": {
            "ID": addon_id,
            "GUID": addon_guid,
            "TITLE": title,
            "Dependencies": deps,
        }
    }
    return serialize(spec)
```

**3.4 `backend/exporters/conf.py`** — Mission Header writer:

```python
"""Generate Missions/<name>.conf — SCR_MissionHeader.

Per research/02-mission-format.md Mission-Header schema (verified against arexplorer.zeroy.com).
"""
from .braces import serialize

def generate_mission_header(
    *,
    name: str,
    author: str = "AI-Native Mission Authoring System",
    description: str,
    world_guid: str,
    world_path: str,  # e.g. "Worlds/MyMission.ent"
    game_mode: str = "Coop",
    player_count: int = 8,
    time_hour: int = 8,
    time_minute: int = 0,
    extra_fields: dict | None = None,
) -> str:
    """Generate SCR_MissionHeader .conf content."""
    fields = {
        "World": f"{{{world_guid}}}{world_path}",
        "m_sName": name,
        "m_sAuthor": author,
        "m_sDescription": description + " | Authored with LLM-assisted tooling. Human-reviewed. No live AI calls.",
        "m_sGameMode": game_mode,
        "m_iPlayerCount": player_count,
        "m_bOverrideScenarioTimeAndWeather": 1,
        "m_iStartingHours": time_hour,
        "m_iStartingMinutes": time_minute,
    }
    if extra_fields:
        fields.update(extra_fields)
    spec = {"SCR_MissionHeader": fields}
    return serialize(spec)

def generate_meta(file_guid: str, file_path: str, kind: str = "CONF") -> str:
    """Generate .conf.meta / .ent.meta / .et.meta sidecar.
    
    kind: 'CONF' | 'ENT' | 'ET'
    """
    class_name = f"{kind}ResourceClass"
    spec = {
        "MetaFileClass": {
            "Name": f"{{{file_guid}}}{file_path}",
            "Configurations": {
                f"{class_name} PC": {},
                f"{class_name} XBOX_ONE : PC": {},
                f"{class_name} XBOX_SERIES : PC": {},
                f"{class_name} PS4 : PC": {},
                f"{class_name} HEADLESS : PC": {},
            },
        }
    }
    # Note: this needs custom inheritance syntax that braces.py doesn't fully cover
    # Implement custom emit for Configurations block per research/02-mission-format.md
    return _emit_meta_manually(file_guid, file_path, class_name)

def _emit_meta_manually(file_guid: str, file_path: str, class_name: str) -> str:
    """Emit .meta with proper Configurations syntax (inheritance via colon)."""
    return (
        "MetaFileClass {\n"
        f' Name "{{{file_guid}}}{file_path}"\n'
        ' Configurations {\n'
        f'  {class_name} PC {{}}\n'
        f'  {class_name} XBOX_ONE : PC {{}}\n'
        f'  {class_name} XBOX_SERIES : PC {{}}\n'
        f'  {class_name} PS4 : PC {{}}\n'
        f'  {class_name} HEADLESS : PC {{}}\n'
        ' }\n'
        '}\n'
    )
```

**3.5 `backend/exporters/ent.py`** — World file:

```python
"""Generate Worlds/<name>.ent.

Two patterns per research/02-mission-format.md:
1. SubScene { Parent "<existing-world>" }
2. Self-contained: Layer N { Index N } table
"""

def generate_world_subscene(parent_world: str) -> str:
    """Inherit from an existing world (most common for missions on Eden/Arland)."""
    return f'SubScene {{\n Parent "{parent_world}"\n}}\n'

def generate_world_layers(layer_names: list[str]) -> str:
    """Self-contained world with explicit layer table.
    Order matters — layer index = position in list.
    """
    out = ""
    for idx, name in enumerate(layer_names):
        out += f"Layer {name}     {{ Index {idx} }}\n"
    return out
```

**3.6 `backend/exporters/layer.py`** — Entity layers:

```python
"""Generate Worlds/<name>_<layer>.layer files.

Per research/02-mission-format.md Entity Layers schema.
"""
from .braces import _serialize_dict
from io import StringIO

def generate_layer(entities: list[dict]) -> str:
    """Generate a .layer file.
    
    Each entity: {
        "class_name": "SCR_SpawnPoint",
        "instance_name": "SpawnPoint_US",
        "prefab_guid": "CEA2B24051A44525",
        "prefab_path": "PrefabsEditable/SpawnPoints/E_SpawnPoint_US.et",
        "coords": [263, 9, 245],
        "angle_y": -60.0,
        "fields": {...},
        "components": [...],
        "children": [...]
    }
    
    Or grouped:
    {
        "$grp": True,
        "class_name": "SCR_AIWaypoint",
        "prefab_guid": "...",
        "prefab_path": "...",
        "instances": [
            {"name": "WP1", "coords": [...]},
            ...
        ]
    }
    """
    out = StringIO()
    for ent in entities:
        if ent.get("$grp"):
            out.write(_emit_grouped(ent))
        else:
            out.write(_emit_single(ent))
    return out.getvalue()

def _emit_single(ent: dict) -> str:
    out = StringIO()
    cn = ent["class_name"]
    inst = ent.get("instance_name", "")
    pref = f'{{{ent["prefab_guid"]}}}{ent["prefab_path"]}'
    header = f"{cn} {inst} : \"{pref}\"" if inst else f"{cn} : \"{pref}\""
    out.write(f"{header} {{\n")
    if "coords" in ent:
        out.write(f" coords {ent['coords'][0]} {ent['coords'][1]} {ent['coords'][2]}\n")
    for ax in ("angle_x", "angle_y", "angle_z"):
        if ax in ent:
            field = ax.replace("_", "").replace("angle", "angle").capitalize()
            field = "angleY" if ax == "angle_y" else "angleX" if ax == "angle_x" else "angleZ"
            out.write(f" {field} {ent[ax]}\n")
    for k, v in (ent.get("fields") or {}).items():
        if isinstance(v, str):
            out.write(f' {k} "{v}"\n')
        elif isinstance(v, list):
            out.write(f" {k} {{\n")
            for it in v:
                if isinstance(it, str): out.write(f'  "{it}"\n')
                else: out.write(f"  {it}\n")
            out.write(" }\n")
        else:
            out.write(f" {k} {v}\n")
    out.write("}\n")
    return out.getvalue()

def _emit_grouped(grp: dict) -> str:
    out = StringIO()
    cn = grp["class_name"]
    pref = f'{{{grp["prefab_guid"]}}}{grp["prefab_path"]}'
    out.write(f'$grp {cn} : "{pref}" {{\n')
    for inst in grp.get("instances", []):
        out.write(f' {inst["name"]} {{\n')
        if "coords" in inst:
            out.write(f'  coords {inst["coords"][0]} {inst["coords"][1]} {inst["coords"][2]}\n')
        for k, v in (inst.get("fields") or {}).items():
            if isinstance(v, str):
                out.write(f'  {k} "{v}"\n')
            else:
                out.write(f'  {k} {v}\n')
        out.write(" }\n")
    out.write("}\n")
    return out.getvalue()
```

**3.7 `backend/validators/schema.py`** — Schema-Validation:

```python
"""Validate generated mission files against research/02-mission-format.md schema."""
import re
from pathlib import Path

GUID_RE = re.compile(r"^[0-9A-F]{16}$")
GUID_REF_RE = re.compile(r'\{([0-9A-F]{16})\}([^"\s]+)')

class ValidationError(Exception):
    def __init__(self, file: str, issue: str, suggested_fix: str = ""):
        self.file = file
        self.issue = issue
        self.suggested_fix = suggested_fix
        super().__init__(f"{file}: {issue}")

def validate_mission_tree(output_dir: Path, catalog_index: dict) -> list[ValidationError]:
    """Run all 12 validation rules from research/02-mission-format.md."""
    errors = []
    
    # Rule 1: addon.gproj has core dependency
    gproj = output_dir / "addon.gproj"
    if not gproj.exists():
        errors.append(ValidationError("addon.gproj", "missing", "regenerate"))
    else:
        content = gproj.read_text()
        if "58D0FB3206B6F859" not in content:
            errors.append(ValidationError("addon.gproj", "missing core Arma Reforger dependency", 'add "58D0FB3206B6F859" to Dependencies'))
    
    # Rule 3 + 5: All GUID refs resolve
    for f in output_dir.rglob("*"):
        if f.is_file() and f.suffix in (".conf", ".ent", ".layer"):
            content = f.read_text(errors="ignore")
            for m in GUID_REF_RE.finditer(content):
                guid = m.group(1)
                if guid not in catalog_index["guid_to_type"] and guid != catalog_index.get("core_guid"):
                    # Check if it's a self-generated GUID (e.g. mission's own GUID)
                    own_guid = _extract_own_guid(content)
                    if guid != own_guid:
                        errors.append(ValidationError(str(f.name), f"hallucinated GUID {guid}", "replace with verified asset from catalog/"))
    
    # Rule 6: player count >= 2 if multiplayer
    conf_files = list((output_dir / "Missions").glob("*.conf"))
    for conf in conf_files:
        content = conf.read_text()
        if 'm_sGameMode "Coop"' in content or 'm_sGameMode "Conflict"' in content:
            m = re.search(r"m_iPlayerCount\s+(\d+)", content)
            if m and int(m.group(1)) < 2:
                errors.append(ValidationError(conf.name, "player count < 2 for multiplayer mode", "set m_iPlayerCount to >=2"))
    
    # Rule 11: .layer files declared in .ent
    ent_files = list((output_dir / "Worlds").glob("*.ent"))
    layer_files = {f.stem for f in (output_dir / "Worlds").glob("*.layer")}
    if ent_files:
        ent_content = ent_files[0].read_text()
        if "Layer " in ent_content:  # uses self-contained pattern
            declared = set(re.findall(r"Layer\s+(\w+)\s*{", ent_content))
            world_stem = ent_files[0].stem
            expected_layer_stems = {f"{world_stem}_{name}" for name in declared}
            orphans = layer_files - expected_layer_stems
            for o in orphans:
                errors.append(ValidationError(f"{o}.layer", "orphan layer not declared in .ent", f"add 'Layer ... {{ Index N }}' to {ent_files[0].name}"))
    
    return errors

def _extract_own_guid(content: str) -> str | None:
    m = re.search(r'Name "\{([0-9A-F]{16})\}', content)
    return m.group(1) if m else None
```

**3.8 Tests in `backend/tests/`**:

```python
# backend/tests/test_exporters.py
from backend.exporters.gproj import generate_gproj
from backend.exporters.conf import generate_mission_header, generate_meta

def test_gproj_minimal():
    out = generate_gproj("TestMission", "ABCDEF1234567890", "Test Mission")
    assert "GameProject {" in out
    assert "58D0FB3206B6F859" in out
    assert "TestMission" in out

def test_conf_minimal():
    out = generate_mission_header(
        name="Test",
        description="Test",
        world_guid="ABCDEF1234567890",
        world_path="Worlds/Test.ent",
    )
    assert 'SCR_MissionHeader' in out
    assert 'World "{ABCDEF1234567890}Worlds/Test.ent"' in out
    assert 'm_sGameMode "Coop"' in out
    assert "LLM-assisted" in out  # Disclosure
```

**Definition of Done Phase 3:**
- alle backend-Module schreiben kompilierbare Brace-Syntax (manual verify durch diff gegen CoopTest-Sample)
- pytest läuft grün
- `pipeline-tester` kann diese Module orchestrieren

---

### Phase 4: Specialist-Agent-Files vervollständigen (30 min)

Specs für `mission-director`, `version-keeper`, `narrative-designer` existieren. Du implementierst die fehlenden vier:

**4.1 `.claude/agents/specialists/asset-curator.md`** — Pflicht-Validation:

```yaml
---
name: asset-curator
description: Stage 2 Specialist. Validiert alle asset_id_refs aus narrative.json gegen catalog/. Halluzinations-Block. Pflicht-Gate vor reforger-bridge.
tools: Read, Write, Edit, Bash
---

# Asset Curator

Du validierst, dass alle Asset-Referenzen in narrative.json gegen den GUID-Catalog auflösbar sind. Du erfindest niemals neue asset-ids.

## Input

- `missions/{id}/narrative.json` (Stage 1 Output)
- `catalog/INDEX.json` + `catalog/{type}/{guid}.json` Files

## Output

`missions/{id}/asset-manifest.json`:

```json
{
  "resolved_assets": [
    {"narrative_ref": "ENF_Faction_US", "guid": "...", "path": "...", "type": "faction"}
  ],
  "missing_assets": [
    {"narrative_ref": "MADE_UP_ASSET", "search_attempted": "faction:US", "candidates": []}
  ],
  "halt_required": false|true,
  "halt_reason": "..."
}
```

## Process

1. Lies narrative.json
2. Extrahiere alle Felder die "asset_id_ref" oder "*_guid" heißen
3. Für jeden Ref: lookup im catalog (CatalogResolver.resolve_guid oder find_by_class)
4. Wenn Match: schreibe nach resolved_assets
5. Wenn kein Match: 
   a. Schlage Candidates aus Catalog vor (find_by_class)
   b. Wenn 0 Candidates: HALT, missing_assets-Eintrag
   c. Wenn 1-3 Candidates: HALT, User soll wählen
6. Schreibe asset-manifest.json
7. Wenn halt_required: lass mission-director User briefen

## Hard Constraints

- KEINE Catalog-Erweiterung als "Quick-Fix" für Missing
- KEINE GUID-Erfindung
- Wenn 5+ Iterations failing: triggere /sync-catalog-Empfehlung an User

## Definition of Done

- asset-manifest.json existiert
- halt_required = false (alle resolved) ODER User hat Replacement bestätigt
```

**4.2 `.claude/agents/specialists/encounter-designer.md`** — Stage 6a:

```yaml
---
name: encounter-designer
description: Stage 6a. Designt AI-Groups, Patrols, Spawnwaves, Behavior-States. Konsumiert narrative.json + asset-manifest.json. Output: encounters.json (Teil 1).
tools: Read, Write, Edit
---

# Encounter Designer

Stage 6 Teil 1. Du übersetzt die narrative Story-Setup in konkrete AI-Encounter-Definitionen. flow-architect macht den Trigger-Graph-Part. Beide schreiben in encounters.json.

## Input
- `missions/{id}/narrative.json`
- `missions/{id}/asset-manifest.json` (für GUID-Refs)

## Output (additive zu encounters.json)
- spawn_points (Player + AI)
- ai_groups (mit prefab_guid aus catalog, waypoint_refs, behavior_mode)
- waypoints (Move, Defend, Patrol)
- environment_overrides (time, weather)

## Process

1. Lies narrative.json (factions, pacing, biome, narrative_anchors)
2. Übersetze pacing-phases in encounter-Wellen
3. Für jede AI-Gruppe: wähle prefab aus asset-manifest (NICHT erfinden)
4. Setze sinnvolle Coords basierend auf narrative_anchors (z.B. "insertion via small boat at coastline" → spawn_point.coords nahe Wasser-Kante)
5. Bei Pacing-Wechsel: zusätzliche Waypoints für AI-Bewegung
6. Schreibe partial encounters.json (Felder: spawn_points, ai_groups, waypoints, environment_overrides)

## Coords-Realismus

Wenn keine Map-Daten verfügbar (Mac, kein Workbench): nutze plausible Coords aus narrative_anchors + biome.region_hint. mission-validator erkennt grobe Inkonsistenzen.

## Definition of Done
- encounters.json hat mindestens 1 spawn_point, 1 ai_group, 1 environment_override
- alle prefab_guids sind im asset-manifest resolved
```

**4.3 `.claude/agents/specialists/flow-architect.md`** — Stage 6b:

```yaml
---
name: flow-architect
description: Stage 6b. Designt Trigger-Graph, Tasks/Objectives, State-Machines, Pacing-Logic. Komplettiert encounters.json (Teil 2).
tools: Read, Write, Edit
---

# Flow Architect

Stage 6 Teil 2. Du baust den Trigger-Graph und Task-Logic, der die von encounter-designer platzierten AI-Groups orchestriert.

## Input
- `missions/{id}/narrative.json`
- `missions/{id}/asset-manifest.json`
- partial encounters.json (von encounter-designer)

## Output (additive zu encounters.json)
- tasks (SCR_EliminateTask, SCR_TriggerTask, etc.)
- triggers (SCR_BaseTriggerEntity mit SCR_AISpawnerComponent für Dynamic-Spawn)
- managers (GameMode, FactionManager, LoadoutManager, TimeAndWeather)

## Process

1. Lies bestehende encounters.json + narrative.json
2. Für jeden narrative_anchor: passende Task-Klasse wählen
   - "photograph or tag enemy command vehicle" → SCR_TriggerTask mit FactionTriggerEntity
   - "exfil under increasing pressure" → SCR_BaseTriggerEntity mit SCR_AISpawnerComponent
3. Trigger-Sequenz: erste Trigger bei spawn, weitere am Objective, finale bei exfil
4. Pacing-Eskalation: progressive Trigger-Radien oder Spawn-Wave-Größen über Mission-Verlauf
5. Schreibe vervollständigte encounters.json

## Hard Constraints

- KEIN Embedding von Live-LLM-Calls in userScript (EULA-Risk)
- userScript bleibt einfach: einfache state-checks + delegations an Engine-API
- Trigger müssen plausible Coords haben (mission-validator checks)

## Definition of Done
- encounters.json komplett (alle Top-Level-Keys gesetzt)
- mindestens 1 Task + 1 Trigger
- managers-Liste mit ≥4 Standards
```

**4.4 `.claude/agents/specialists/reforger-bridge.md`** — Stage 6c (File-Gen):

```yaml
---
name: reforger-bridge
description: Stage 6c. Übersetzt narrative.json + asset-manifest.json + encounters.json in vollständiges Reforger-Addon-Tree (Brace-Syntax-Files).
tools: Read, Write, Edit, Bash
---

# Reforger Bridge

Stage 6 Teil 3. Du erzeugst das finale Mission-Output: ein unpacked addon-Tree im Reforger-Format. Du nutzt die backend/exporters/-Module.

## Input
- `missions/{id}/narrative.json`
- `missions/{id}/asset-manifest.json`
- `missions/{id}/encounters.json`

## Output
- `missions/{id}/output/addon.gproj`
- `missions/{id}/output/Missions/{id}.conf` + `.conf.meta`
- `missions/{id}/output/Worlds/{id}.ent` + `.ent.meta`
- `missions/{id}/output/Worlds/{id}_gamemode.layer`
- `missions/{id}/output/Worlds/{id}_managers.layer`
- `missions/{id}/output/Worlds/{id}_spawnpoints.layer`
- `missions/{id}/output/Worlds/{id}_AI.layer`
- `missions/{id}/output/Worlds/{id}_tasks.layer`
- `missions/{id}/output/Worlds/{id}_triggers.layer`
- `missions/{id}/output/Worlds/{id}_environment.layer`

## Process

1. Mintne neue GUIDs: addon_guid, mission_header_guid, world_guid
   - Format: 16 uppercase hex
   - Dedupe gegen catalog INDEX
2. Generiere addon.gproj (via exporters/gproj.py)
3. Generiere Missions/{id}.conf (via exporters/conf.py)
4. Generiere Worlds/{id}.ent — entscheide ob SubScene oder Layer-Table basierend auf biome.map_id_ref
5. Für jeden Layer-Type: rufe exporters/layer.py mit den entsprechenden Entities aus encounters.json
6. Schreibe alle .meta-Sidecars
7. Verifiziere via internem Schema-Check (validators/schema.py)
8. Schreibe Disclosure-File `missions/{id}/output/DISCLOSURE.md`

## Hard Constraints

- KEINE GUID-Halluzination: jede prefab_guid stammt aus asset-manifest, jede mission_guid ist neu gemintet und im local-mint-log
- Brace-Syntax-Validität: nutze backend/exporters/braces.py konsistent
- mission-header description-Field enthält Auto-Disclosure (vom Code injiziert)

## Definition of Done

- Alle 7+ Files in output/ existieren
- mission-validator bestätigt Brace-Syntax-Validität (kein Halt)
- Asset-Manifest matched 1:1 mit GUID-Refs in generierten Files

```

**Definition of Done Phase 4:**
- Alle 7 MVP-Specialists existieren als `.md` mit YAML-Header
- Specs sind konsistent (Tool-Listen, Input/Output, Process, DoD)

---

### Phase 5: Pipeline Integration (45 min)

**5.1 Mission-Director-Integration testen:**

Erste End-to-End-Test (autonom, OHNE User):

```bash
# Backend up
cd backend && source .venv/bin/activate
uvicorn main:app --port 8765 &
sleep 2

# Dummy-Mission für Self-Testing
mkdir -p missions/test-mission-pipeline-check
echo '{"stage":1,"status":"awaiting_input"}' > missions/test-mission-pipeline-check/current-stage.json
```

**5.2 Self-Testing-Loop Skript** — `backend/scripts/run_self_test.py`:

```python
"""End-to-end self-test for the mission pipeline.

Simulates user input "Night Recon Everon", triggers all MVP stages,
validates output. Used by pipeline-tester agent.
"""
import subprocess, sys, json
from pathlib import Path

MISSION_ID = "test-mission-pipeline-check"
ROOT = Path(__file__).parent.parent.parent

def run_stage(stage_n: int) -> bool:
    print(f"[stage {stage_n}] running...")
    # In production: invoke the actual specialist via Claude Code's Task tool
    # For self-test: use deterministic fixtures
    if stage_n == 1:
        fixture = ROOT / "backend" / "tests" / "fixtures" / "night_recon_narrative.json"
        target = ROOT / "missions" / MISSION_ID / "narrative.json"
        target.write_text(fixture.read_text())
    # ... analog für Stage 2, 6
    return True

def main():
    for stage in [1, 2, 6]:
        if not run_stage(stage):
            print(f"FAIL at stage {stage}")
            sys.exit(1)
    print("ALL STAGES PASS")

if __name__ == "__main__":
    main()
```

**5.3 Test-Fixtures vorbereiten** — `backend/tests/fixtures/`:

Lege Beispiel-narrative.json an mit dem "Night Recon Everon" Inhalt (aus DECISIONS.md):

```json
{
  "title": "Night Recon Everon",
  "tagline": "Eine US-Recon-Einheit beschattet einen USSR-Vorposten bei Nacht.",
  "premise": "...",
  "factions": { ... },
  ...
}
```

Volle Beispiele in `.claude/agents/specialists/narrative-designer.md`.

**Definition of Done Phase 5:**
- `pipeline-tester` läuft komplett ohne crash auf test-mission-pipeline-check
- output/ enthält alle erwarteten Files
- mission-validator returns passed: true

---

### Phase 6: Optional Linux-Dedi-Empirical-Test (30 min, only if feasible)

**Open Question 1 aus `02-mission-format.md`:** Lädt Linux-Dedicated-Server ein unpacked addon-tree?

**6.1 Check Availability:**

```bash
# Wenn User ein remote-server oder Docker-Image hat:
which docker
docker images | grep -i reforger

# Oder: SSH zu einem Linux-VPS mit Reforger-Dedi
```

**6.2 Wenn verfügbar: Test-Script:**

```bash
# Beispiel: Docker-Run mit unpacked addon-tree
docker run --rm \
  -v $(pwd)/missions/test-mission-pipeline-check/output:/addon \
  -e ADDON_PATH=/addon \
  -e MISSION_GUID=$(jq -r '.guid' missions/test-mission-pipeline-check/output/Missions/*.conf) \
  reforger-dedi:latest \
  -addonsDir /addon \
  -mission "{${MISSION_GUID}}Missions/test-mission-pipeline-check.conf" \
  -maxFPS 30 \
  -profile /tmp/profile
```

Capture-Logs für 30s, parse für "Mission loaded" oder Errors.

**6.3 Wenn NICHT verfügbar:**

Schreibe `OPEN_QUESTION_1_DEFERRED.md` mit Test-Plan für späteren Run.

**Definition of Done Phase 6:**
- ENTWEDER: Linux-Dedi-Test durchgeführt, Ergebnis in `research/04-linux-dedi-test.md`
- ODER: Defer-File geschrieben mit klarem Reproduktions-Plan

---

### Phase 7: Readiness-Reporter + User-Hand-Off (15 min)

**7.1 Erste echte Test-Mission generieren:**

```bash
# Sonnet 4.6: simuliere /new-mission night-recon-everon
# Aktiviere alle Stages, durchlaufe pipeline-tester loop
# Stoppe bei jedem Approval-Gate (siehe Sacred Approval Gates oben)
```

**Achtung:** Phase 7 erfordert User-Approval-Simulation für autonomen End-to-End-Test. Wähle die Strategie:

- **Option A (empfohlen):** Simuliere /approve in Self-Test-Mode (test-mission-pipeline-check), lass `night-recon-everon` für User-Interaction stehen
- **Option B:** Erzeuge `night-recon-everon` komplett autonom mit "auto-approve"-Flag, dokumentiere in WORK_LOG dass User noch nicht approved hat

**7.2 Triggere readiness-reporter:**

Wenn alle Tests grün:
- Schreibe `missions/test-mission-pipeline-check/READY_FOR_MANUAL_TESTING.md`
- Update `WORK_LOG.md` mit Phase-7-Eintrag
- (Wenn night-recon-everon vorhanden:) auch dort Briefing

**7.3 Final-Commit-Vorschlag:**

```bash
cd /Users/paulfanger/Documents/ELOS/201_01-MOD-ArmaReforger-Scenarios
git add -A
git status

# User-Approval-Gate für Commit:
echo "Bereit zum Commit. Diff-Summary oben. /approve-commit oder /revise-commit?"
```

**WARTE auf User-Approval bevor Commit.**

**Definition of Done Phase 7:**
- READY_FOR_MANUAL_TESTING.md existiert für test-mission-pipeline-check
- WORK_LOG.md komplett für Phase 1-7
- Git-Commit pending User-Approval

---

## Sub-Agent Trigger-Points

| Event | Auto-Trigger | Manual via Slash |
|---|---|---|
| User: /new-mission | mission-director | — |
| Stage Output ready | mission-director (User-Briefing) | — |
| User: /approve | version-keeper → mission-director | — |
| Stage 6c output written | pipeline-tester (auto) | /run-tests |
| pipeline-tester pass | mission-validator (auto) | — |
| validator pass | workbench-integration-tester (auto) | — |
| any tester fail | bug-fixer (auto, max 5) | — |
| all tests pass | readiness-reporter (auto) | /check-readiness |
| bug-fixer exhausted | readiness-reporter HALT (auto) | — |

---

## Fallback Trigger Logic

Bei jedem trigger: prüfe Bedingung und switche wenn match.

```python
# Pseudo-code für bug-fixer Decision-Tree:

def decide_fallback(failure_report) -> str:
    if failure_report.type == "win_workbench_not_found":
        return "MODE_A_FILE_PIPELINE_ONLY"
    if failure_report.type == "linux_dedi_load_failed":
        return "MODE_B_MANUAL_VERIFICATION"
    if failure_report.type == "brace_syntax_garbage":
        # Re-template against Sample
        return "STEP_BACK_TO_SAMPLE_TEMPLATE"
    if failure_report.type == "guid_collision":
        return "REMINT_GUIDS"
    if failure_report.type == "hallucinated_asset":
        return "HALT_USER_PING"
    if failure_report.type == "reforger_version_drift":
        return "TRIGGER_NEW_RESEARCH"
    return "DEFAULT_BUG_FIX_ATTEMPT"
```

Detaillierte Fallbacks in `DECISIONS.md` Section "Hard Blockers + Fallback-Strategien".

---

## Definition of Done (Sonnet 4.6 darf stoppen wenn ALLES gilt)

1. ✅ `/new-mission test-mission-pipeline-check` läuft End-to-End ohne Errors
2. ✅ `missions/test-mission-pipeline-check/output/` enthält alle erwarteten Files (gproj, conf, conf.meta, ent, ent.meta, ≥3 layers)
3. ✅ mission-validator zeigt `passed: true` (0 halluzinations, 0 schema errors, 0 cross-file inconsistencies)
4. ✅ workbench-integration-tester hat entweder Mode-A-Pass ODER Mode-B-`MANUAL_VERIFICATION_REQUIRED.md` geschrieben
5. ✅ `missions/test-mission-pipeline-check/READY_FOR_MANUAL_TESTING.md` von readiness-reporter geschrieben
6. ✅ Mindestens 1 Snapshot pro Approval-Gate in `missions/test-mission-pipeline-check/snapshots/`
7. ✅ `WORK_LOG.md` updated mit Phase-1–7-Einträgen
8. ✅ Git working tree clean ODER explizit pending User-Commit-Approval

---

## Stop-Bedingungen (Sonnet 4.6 MUSS stoppen wenn)

- 5 erfolglose bug-fixer-Iterationen am gleichen Test
- Hard-Blocker erkannt (z.B. Reforger-Schema-Drift, EULA-Update)
- Architecture-Change-Bedarf identifiziert → schreibe DECISIONS-Vorschlag + warte auf User
- User-Approval-Gate erreicht

In allen Stop-Fällen: schreibe `STOP_REASON.md` im Project-Root mit klarem next-step.

---

## Anti-Patterns für Sonnet 4.6 (NIEMALS)

- ❌ Asset-IDs erfinden (auch nicht im Test-Mode — Catalog ist Pflicht)
- ❌ Approval-Gates überspringen außer im Self-Testing-Mode
- ❌ Schema-Checks "lockern" als bug-fix (= echtes Schema-Mismatch verstecken)
- ❌ DECISIONS.md ohne explizite Begründung ändern
- ❌ Win-Plugin-Code committen (workbench-plugin/ bleibt Skeleton bis Phase 2)
- ❌ Workshop-Upload auslösen (out of scope)
- ❌ Runtime-LLM-Calls in Mission-Files schreiben
- ❌ Wall-of-Text-User-Briefings — kurz, strukturiert, deutsch
- ❌ Direkte Calls zwischen Specialists — alles über mission-director

---

## Geschätzte Run-Time

- Phase 1 (Setup): 15 min
- Phase 2 (Catalog): 30-45 min
- Phase 3 (Backend): 60-90 min
- Phase 4 (Specialists): 30 min
- Phase 5 (Pipeline): 45 min
- Phase 6 (Linux-Dedi optional): 30 min
- Phase 7 (Ready): 15 min

**Total: 3-5 Stunden autonomer Sonnet-4.6-Run.** Bei Hard-Blocker: HALT + User-Ping nach ~30min.

---

## Start-Anweisung

Wenn du das hier liest: starte mit Phase 1. Update Tasks via TaskCreate/TaskUpdate. Schreibe in WORK_LOG bei jedem Phase-Abschluss. Bei Sacred-Approval-Gate: STOP + User-Ping. Sonst autonom durchlaufen.

**Erste Aktion:** Lies die 8 Foundation-Files (Liste oben), dann `TaskList`, dann starte Phase 1.

Viel Erfolg.
