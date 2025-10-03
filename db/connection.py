"""Database connection helper.

Provides a shared sqlite3 connection for tests and local runs. The module
keeps a single connection instance which can be initialized either in-memory
or backed by the `autofire.db` file.
"""

from __future__ import annotations

import sqlite3

from . import coverage_tables, schema

_connection: sqlite3.Connection | None = None


def initialize_database(in_memory: bool = True) -> None:
    """Initialize the shared database connection.

    Args:
        in_memory: When True, use an in-memory SQLite database. Otherwise use
            the on-disk `autofire.db` file in the repo root.
    """
    global _connection
    if _connection is not None:
        return

    if in_memory:
        _connection = sqlite3.connect(":memory:")
    else:
        _connection = sqlite3.connect("autofire.db")

    _connection.row_factory = sqlite3.Row

    # Ensure schema and lookup data exist for tests and local runs.
    schema.create_schema_tables(_connection)
    coverage_tables.create_tables(_connection)
    coverage_tables.populate_tables(_connection)
    _connection.commit()


def get_connection() -> sqlite3.Connection:
    """Return the initialized shared sqlite3.Connection.

    Raises:
        RuntimeError: If the connection has not been initialized.
    """
    if _connection is None:
        raise RuntimeError("Database not initialized. Call initialize_database() first.")
    return _connection


def close_connection() -> None:
    """Close and clear the shared connection."""
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None
