#!/usr/bin/env python3
"""
Migrate spin_database.py hardcoded dict → SQLite database.

Run once:  python3 backend/migrate_to_sqlite.py
Output:    backend/substances.db
"""
import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "substances.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS substances (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL UNIQUE,
    cas             TEXT    NOT NULL,
    formula         TEXT    NOT NULL,
    smiles          TEXT    NOT NULL,
    mw              REAL    NOT NULL,

    -- Environmental fate half-lives (days)
    degT50_soil     REAL    NOT NULL,
    degT50_water    REAL    NOT NULL,
    degT50_sediment REAL    NOT NULL,

    -- Sorption
    koc             REAL    NOT NULL,
    kfoc            REAL    NOT NULL,
    freundlich_n    REAL    NOT NULL,

    -- Physicochemical
    vapor_pressure  REAL    NOT NULL,
    henry_const     REAL    NOT NULL,
    solubility      REAL    NOT NULL,
    pka             REAL,           -- nullable
    logP            REAL    NOT NULL,

    -- Molecular descriptors
    n_atoms         INTEGER NOT NULL,
    n_heavy         INTEGER NOT NULL,
    hbd             INTEGER NOT NULL,
    hba             INTEGER NOT NULL,
    n_rings         INTEGER NOT NULL,
    n_rotatable     INTEGER NOT NULL,

    -- Regulatory
    cls             TEXT    NOT NULL,
    status          TEXT    NOT NULL,

    -- Metadata
    created_at      TEXT    DEFAULT (datetime('now')),
    updated_at      TEXT    DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_substances_name ON substances(name);
CREATE INDEX IF NOT EXISTS idx_substances_cas ON substances(cas);
CREATE INDEX IF NOT EXISTS idx_substances_cls ON substances(cls);
"""

# Column order for INSERT (matching SUBSTANCES dict keys)
COLUMNS = [
    "name", "cas", "formula", "smiles", "mw",
    "degT50_soil", "degT50_water", "degT50_sediment",
    "koc", "kfoc", "freundlich_n",
    "vapor_pressure", "henry_const", "solubility", "pka", "logP",
    "n_atoms", "n_heavy", "hbd", "hba", "n_rings", "n_rotatable",
    "cls", "status",
]


def migrate():
    # Import the original hardcoded data
    from backend.spin_database import SUBSTANCES as LEGACY_DATA

    if os.path.exists(DB_PATH):
        os.rename(DB_PATH, DB_PATH + ".bak")
        print(f"  Backed up existing DB to {DB_PATH}.bak")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(SCHEMA)

    placeholders = ", ".join(["?"] * len(COLUMNS))
    col_names = ", ".join(COLUMNS)
    insert_sql = f"INSERT OR REPLACE INTO substances ({col_names}) VALUES ({placeholders})"

    count = 0
    for sub in LEGACY_DATA:
        values = []
        for col in COLUMNS:
            val = sub.get(col)
            # hbd can be 0 which is falsy but valid
            if val is None and col != "pka":
                val = 0 if col in ("hbd", "hba", "n_rings", "n_rotatable") else val
            values.append(val)
        conn.execute(insert_sql, values)
        count += 1

    conn.commit()

    # Verify
    cursor = conn.execute("SELECT COUNT(*) FROM substances")
    db_count = cursor.fetchone()[0]
    assert db_count >= count - 5, f"Expected ~{count}, got {db_count} (some duplicates removed)"

    # Print summary
    cursor = conn.execute("SELECT cls, COUNT(*) FROM substances GROUP BY cls ORDER BY COUNT(*) DESC")
    print(f"\n  Migrated {db_count} substances to {DB_PATH}")
    print(f"  Schema: {len(COLUMNS)} columns + id + timestamps")
    print(f"\n  By class:")
    for cls, n in cursor.fetchall():
        print(f"    {cls:30s} {n:3d}")

    conn.close()
    print(f"\n  Migration complete!")


if __name__ == "__main__":
    print("=" * 50)
    print("  SPIN Database → SQLite Migration")
    print("=" * 50)
    migrate()
