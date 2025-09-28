# db/connection.py
import sqlite3

from . import coverage_tables, schema

_connection: sqlite3.Connection | None = None


def initialize_database(in_memory: bool = True):
    """Initializes the shared database connection."""
    global _connection
    if _connection:
        return

    if in_memory:
        _connection = sqlite3.connect(":memory:")
    else:
        # This path can be configured later
        _connection = sqlite3.connect("autofire.db")

    schema.create_schema_tables(_connection)
    coverage_tables.create_tables(_connection)
    coverage_tables.populate_tables(_connection)
    _connection.commit()

def get_connection() -> sqlite3.Connection:
    """Returns the shared database connection."""
    if not _connection:
        raise RuntimeError(
            "Database not initialized. Call initialize_database() first."
        )
    return _connection

def close_connection():
    """Closes the shared database connection."""
    global _connection
    if _connection:
        _connection.close()
        _connection = None
