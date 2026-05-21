"""
Episodic memory store backed by SQLite FTS5.

Stores turn-level summaries (what happened, decisions made, lessons learned)
so future sessions can retrieve relevant context without re-reading all files.

~50 LOC core, importable as a pure-Python module.

Usage:
    from backend.memory.episodic import EpisodicMemory

    mem = EpisodicMemory()
    mem.log("turn-4", "pc", "Validate 3/3 PASS after Author-fix. Junction setup stable.")
    results = mem.search("validate pass")
"""

from __future__ import annotations

import sqlite3
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Default DB path (relative to repo root)
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).parents[2]
DEFAULT_DB_PATH = _REPO_ROOT / "backend" / "memory" / "episodic.db"


class EpisodicMemory:
    """SQLite FTS5-backed episodic log with full-text search."""

    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._init_db()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _init_db(self) -> None:
        """Create FTS5 virtual table if not yet present."""
        self._conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS episodes USING fts5(
                episode_id,
                side,        -- 'mac' | 'pc' | 'both'
                summary,     -- free-text summary
                tags,        -- space-separated tags for boosted retrieval
                created_at,
                tokenize = 'unicode61'
            )
        """)
        self._conn.commit()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def log(
        self,
        episode_id: str,
        side: str,
        summary: str,
        tags: str = "",
    ) -> None:
        """Append an episode to the store."""
        created_at = str(int(time.time()))
        self._conn.execute(
            "INSERT INTO episodes VALUES (?, ?, ?, ?, ?)",
            (episode_id, side, summary, tags, created_at),
        )
        self._conn.commit()

    def search(self, query: str, limit: int = 5) -> list[dict]:
        """Full-text search; returns up to `limit` matching episodes."""
        cur = self._conn.execute(
            """
            SELECT episode_id, side, summary, tags, created_at,
                   bm25(episodes) AS score
            FROM episodes
            WHERE episodes MATCH ?
            ORDER BY score
            LIMIT ?
            """,
            (query, limit),
        )
        return [
            {
                "episode_id": row[0],
                "side": row[1],
                "summary": row[2],
                "tags": row[3],
                "created_at": int(row[4]),
                "score": row[5],
            }
            for row in cur.fetchall()
        ]

    def all_episodes(self, limit: int = 100) -> list[dict]:
        """Return all episodes in insertion order (newest first)."""
        cur = self._conn.execute(
            "SELECT episode_id, side, summary, tags, created_at FROM episodes "
            "ORDER BY CAST(created_at AS INTEGER) DESC LIMIT ?",
            (limit,),
        )
        return [
            {
                "episode_id": row[0],
                "side": row[1],
                "summary": row[2],
                "tags": row[3],
                "created_at": int(row[4]),
            }
            for row in cur.fetchall()
        ]

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "EpisodicMemory":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


# ---------------------------------------------------------------------------
# Bootstrap: import existing reflection files as historical episodes
# ---------------------------------------------------------------------------

def bootstrap_from_reflections(
    mem: EpisodicMemory,
    repo_root: Path = _REPO_ROOT,
) -> int:
    """
    One-time import of logs/reflection-turn-*.md files into episodic store.

    Returns number of episodes imported.
    """
    imported = 0
    for path in sorted(repo_root.glob("logs/reflection-turn-*.md")):
        episode_id = path.stem  # e.g. "reflection-turn-5-pc"
        parts = episode_id.split("-")
        side = parts[-1] if parts[-1] in ("mac", "pc") else "both"
        summary = path.read_text(encoding="utf-8")[:500].replace("\n", " ")
        tags = "reflection " + side
        try:
            mem.log(episode_id, side, summary, tags)
            imported += 1
        except Exception:
            pass  # skip duplicates
    return imported
