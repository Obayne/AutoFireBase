### Task: Create Database Connection Manager

**Objective:**

Create a centralized manager for the application's SQLite database connection. This will ensure that all parts of the application share a single, properly initialized database instance.

**Key Steps:**

1.  **Create `db/connection.py`:**
    *   This module will hold a singleton instance of the `sqlite3.Connection`.
    *   It should have an `initialize_database()` function that:
        *   Connects to an in-memory database for now.
        *   Calls `db.schema.create_tables()`.
        *   Calls `db.coverage_tables.create_tables()` and `populate_tables()`.
    *   It should provide a `get_connection()` function that returns the shared connection object.

2.  **Integrate in `main.py`:**
    *   Call `initialize_database()` early in the application's startup sequence in `app/main.py`.

3.  **Refactor `coverage_service.py`:**
    *   Update the functions in `backend/coverage_service.py` to use `db.connection.get_connection()` instead of requiring a `con` argument.

**Acceptance Criteria:**

*   The application starts without errors.
*   The `coverage_service` functions can be called without explicitly passing a connection object.
*   Tests for the `coverage_service` are updated to reflect the new connection management and still pass.
