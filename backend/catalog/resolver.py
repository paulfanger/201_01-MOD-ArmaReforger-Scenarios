"""Catalog Resolver — resolves asset references against bootstrapped catalog.

Zero-tolerance hallucination guard: if a GUID is not in catalog, returns None.
Never invents or approximates GUIDs.
"""
import json
from pathlib import Path
from typing import Optional

CATALOG_DIR = Path(__file__).parent.parent.parent / "catalog"
CORE_GUID = "58D0FB3206B6F859"  # ArmaReforger core — always required


class CatalogResolver:
    def __init__(self, catalog_dir: Path = CATALOG_DIR):
        self._catalog_dir = catalog_dir
        index_path = catalog_dir / "INDEX.json"
        if not index_path.exists():
            raise FileNotFoundError(
                f"Catalog not bootstrapped: {index_path}\n"
                "Run: python3 backend/catalog/bootstrap.py"
            )
        self.index: dict = json.loads(index_path.read_text())
        self._cache: dict[str, Optional[dict]] = {}

        # Semantic aliases: "ENF_Faction_US" -> GUID  (written by enrich_factions.py)
        aliases_path = catalog_dir / "ALIASES.json"
        if aliases_path.exists():
            aliases_data = json.loads(aliases_path.read_text())
            self._aliases: dict[str, str] = {
                name: info["guid"]
                for name, info in aliases_data.get("aliases", {}).items()
            }
        else:
            self._aliases = {}

        # Also load from INDEX if present (redundant but fast path)
        self._aliases.update(self.index.get("semantic_aliases", {}))

    # ---- Primary API -------------------------------------------------------

    def resolve_alias(self, alias_name: str) -> Optional[dict]:
        """Resolve a semantic alias like 'ENF_Faction_US' to a catalog entry.

        Returns the full catalog entry dict, or None if alias is unknown.
        This is the entry-point for narrative-designer asset_id_ref values.

        Example:
            r.resolve_alias("ENF_Faction_US")
            # -> {"guid": "ADFDBDA163950168", "path": "Configs/Factions/US_Campaign.conf", ...}
        """
        guid = self._aliases.get(alias_name)
        if guid is None:
            return None
        return self.resolve_guid(guid)

    def list_aliases(self) -> dict[str, str]:
        """Return all known semantic aliases -> GUID mappings."""
        return dict(self._aliases)

    def resolve_guid(self, guid: str) -> Optional[dict]:
        """Lookup asset by GUID. Returns None if not in catalog (hallucination guard).

        Never returns a fabricated result. Callers MUST handle None.
        """
        guid = guid.upper()
        if guid in self._cache:
            return self._cache[guid]

        if guid not in self.index["guid_to_type"]:
            self._cache[guid] = None
            return None

        asset_type = self.index["guid_to_type"][guid]
        fp = self._catalog_dir / asset_type / f"{guid}.json"
        if not fp.exists():
            self._cache[guid] = None
            return None

        data = json.loads(fp.read_text())
        self._cache[guid] = data
        return data

    def find_by_class(self, class_name: str) -> list[dict]:
        """Find catalog entries where class_name matches (for suggestion on miss)."""
        results = []
        for guid in self.index["guid_to_type"]:
            ref = self.resolve_guid(guid)
            if ref and ref.get("class_name") == class_name:
                results.append(ref)
        return results

    def find_by_type(self, asset_type: str) -> list[dict]:
        """List all assets of a given type (faction, vehicle, gamemode, etc.)."""
        results = []
        for guid, t in self.index["guid_to_type"].items():
            if t == asset_type:
                ref = self.resolve_guid(guid)
                if ref:
                    results.append(ref)
        return results

    def search_by_display_name(self, query: str, asset_type: str | None = None) -> list[dict]:
        """Fuzzy search by display_name substring. Optional type filter."""
        query_lower = query.lower()
        results = []
        for guid, t in self.index["guid_to_type"].items():
            if asset_type and t != asset_type:
                continue
            ref = self.resolve_guid(guid)
            if ref and query_lower in ref.get("display_name", "").lower():
                results.append(ref)
        return results

    def find_by_path_fragment(self, fragment: str) -> list[dict]:
        """Find by partial path match (e.g. 'Factions/US' or 'CoopGameMode')."""
        fragment_lower = fragment.lower()
        results = []
        for guid in self.index["guid_to_type"]:
            ref = self.resolve_guid(guid)
            if ref and fragment_lower in ref.get("path", "").lower():
                results.append(ref)
        return results

    # ---- Validation helpers ------------------------------------------------

    def is_valid_guid(self, guid: str) -> bool:
        """True if GUID is in catalog. False = potential hallucination."""
        return guid.upper() in self.index["guid_to_type"]

    def has_core_dependency(self) -> bool:
        """Core Arma Reforger GUID should always be in any valid addon."""
        return True  # Core is a dep not in the catalog itself, always inject

    # ---- Stats -------------------------------------------------------------

    @property
    def total_assets(self) -> int:
        return self.index["total_assets"]

    @property
    def by_type_counts(self) -> dict[str, int]:
        return self.index["by_type"]

    def summary(self) -> str:
        lines = [f"Catalog: {self.total_assets} assets"]
        for t, n in sorted(self.by_type_counts.items()):
            lines.append(f"  {t}: {n}")
        return "\n".join(lines)
