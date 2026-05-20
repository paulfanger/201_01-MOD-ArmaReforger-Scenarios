"""Generate addon.gproj — the Arma Reforger addon project file.

Per research/02-mission-format.md File-by-File-Anatomy `addon.gproj`:
  - Required: ID (human-readable), GUID (16-hex), TITLE
  - Required: Dependencies containing ArmaReforger core GUID 58D0FB3206B6F859
  - Optional: extra_deps for mod dependencies (DLC, other mods)

Format: Enfusion Brace-Syntax (NOT JSON).
"""
from .braces import INDENT_STEP

CORE_GUID = "58D0FB3206B6F859"  # ArmaReforger core — mandatory dependency


def generate_gproj(
    addon_id: str,
    addon_guid: str,
    title: str,
    extra_deps: list[str] | None = None,
    author: str | None = None,  # kept for back-compat; no longer emitted
) -> str:
    """Generate addon.gproj content.

    Args:
        addon_id: Human-readable ID, e.g. "NightReconEveron" (no spaces)
        addon_guid: 16 uppercase hex chars (minted by GUID minter)
        title: Human-readable title, e.g. "Night Recon Everon"
        extra_deps: Optional list of extra GUID dependencies
        author: DEPRECATED — Enfusion-Schema kennt `Author` nicht; Attribution lebt in DISCLOSURE.md

    Returns:
        String content for addon.gproj file.

    Note:
        Per PC empirical finding (Task 003 commit 655c2f4), `Author` keyword is not
        in Enfusion's gproj schema and causes -validate failure. Attribution moved
        to DISCLOSURE.md (already present per project EULA-compliance).
    """
    deps = [CORE_GUID] + (extra_deps or [])

    out = "GameProject {\n"
    out += f' ID "{addon_id}"\n'
    out += f' GUID "{{{addon_guid}}}"\n'
    out += f' TITLE "{title}"\n'
    out += " Dependencies {\n"
    for dep in deps:
        out += f'  "{dep}"\n'
    out += " }\n"
    out += "}\n"
    return out
