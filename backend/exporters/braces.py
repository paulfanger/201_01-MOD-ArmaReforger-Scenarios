"""Enfusion Brace-Syntax serializer.

Produces files matching the format observed in Reforger reference repos:
  - Reforger-Sample-Coop/SampleCoop/Worlds/*.layer
  - Arma-Reforger-Samples/**/*.conf
  - research/02-mission-format.md Annotated Examples

IMPORTANT: This is NOT JSON. It's Enfusion's custom DSL with significant whitespace.

Format rules (from observation):
  - Top-level: ClassName { ... }
  - Nested: key { ... }
  - Scalars: key "value" | key 42 | key 1 (bool)
  - GUID refs: "{ABCDEF1234567890}path/to.et"
  - Single-space indent step (observed in reference files)
  - No trailing commas (it's not JSON)
"""
from typing import Any
from io import StringIO

INDENT_STEP = " "  # single space, per observed Reforger files


def serialize(obj: Any, level: int = 0) -> str:
    """Serialize a Python dict to Enfusion brace syntax.

    Top-level dict: each key becomes either a class block or a key-value.
    Only dicts are accepted at top level.
    """
    if isinstance(obj, dict):
        return _serialize_dict(obj, level)
    raise ValueError(f"Top-level must be dict, got {type(obj)}")


def _serialize_dict(d: dict, level: int) -> str:
    out = StringIO()
    indent = INDENT_STEP * level

    for key, val in d.items():
        if isinstance(val, dict):
            # Block: key { ... }
            out.write(f"{indent}{key} {{\n")
            out.write(_serialize_dict(val, level + 1))
            out.write(f"{indent}}}\n")

        elif isinstance(val, list):
            # List block: key { items... }
            out.write(f"{indent}{key} {{\n")
            for item in val:
                if isinstance(item, dict):
                    # Anonymous block inside list
                    out.write(_serialize_dict(item, level + 1))
                elif isinstance(item, str):
                    out.write(f"{indent}{INDENT_STEP}{_fmt_str(item)}\n")
                else:
                    out.write(f"{indent}{INDENT_STEP}{item}\n")
            out.write(f"{indent}}}\n")

        elif val is None:
            # Emit empty block
            out.write(f"{indent}{key} {{}}\n")

        else:
            # Scalar
            out.write(f"{indent}{key} {_fmt_scalar(val)}\n")

    return out.getvalue()


def _fmt_scalar(v: Any) -> str:
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, str):
        return _fmt_str(v)
    if isinstance(v, (int, float)):
        return str(v)
    return str(v)


def _fmt_str(s: str) -> str:
    """Strings are always quoted in Enfusion syntax."""
    # Escape any embedded quotes
    escaped = s.replace('"', '\\"')
    return f'"{escaped}"'


# ---- Specialized emitters for patterns that braces.py can't express ----------

def emit_class_block(class_name: str, fields: dict, level: int = 0) -> str:
    """Emit: ClassName { fields... }  (top-level class declaration)"""
    out = StringIO()
    indent = INDENT_STEP * level
    out.write(f"{indent}{class_name} {{\n")
    out.write(_serialize_dict(fields, level + 1))
    out.write(f"{indent}}}\n")
    return out.getvalue()


def emit_meta_configurations(class_name: str) -> str:
    """Emit the Configurations block with platform inheritance.

    Enfusion .meta syntax uses colon inheritance which braces.py can't express.
    Example:
        Configurations {
         CONFResourceClass PC {}
         CONFResourceClass XBOX_ONE : PC {}
         ...
        }
    """
    platforms = [
        ("PC", None),
        ("XBOX_ONE", "PC"),
        ("XBOX_SERIES", "PC"),
        ("PS4", "PC"),
        ("HEADLESS", "PC"),
    ]
    out = StringIO()
    out.write(" Configurations {\n")
    for platform, parent in platforms:
        if parent:
            out.write(f"  {class_name} {platform} : {parent} {{}}\n")
        else:
            out.write(f"  {class_name} {platform} {{}}\n")
    out.write(" }\n")
    return out.getvalue()
