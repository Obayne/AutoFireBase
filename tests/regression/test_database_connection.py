"""Regression test for database connectivity and catalog loading."""


class TestDatabaseConnection:
    """Test that database is properly connected and catalog loads from it."""

    def test_database_initializes_with_data(self):
        """Verify database initializes and contains device catalog data."""
        from db import connection

        connection.initialize_database(in_memory=True)
        conn = connection.get_connection()
        cursor = conn.cursor()

        # Check that tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        assert "manufacturers" in tables
        assert "device_types" in tables
        assert "devices" in tables
        assert "wall_strobe_coverage" in tables
        assert "ceiling_strobe_coverage" in tables

        # Check that tables have data
        cursor.execute("SELECT COUNT(*) FROM manufacturers")
        assert cursor.fetchone()[0] > 0, "manufacturers table should have data"

        cursor.execute("SELECT COUNT(*) FROM device_types")
        assert cursor.fetchone()[0] > 0, "device_types table should have data"

        cursor.execute("SELECT COUNT(*) FROM devices")
        device_count = cursor.fetchone()[0]
        assert device_count > 0, "devices table should have data"

    def test_catalog_loads_from_database(self):
        """Verify catalog.load_catalog() loads devices from database."""
        from app import catalog
        from db import connection

        # Initialize database
        connection.initialize_database(in_memory=True)

        # Load catalog
        devices = catalog.load_catalog()

        # Should have devices
        assert len(devices) > 0, "Catalog should load devices"

        # Devices should have required fields
        for device in devices:
            assert "name" in device
            assert "type" in device
            assert "manufacturer" in device
            assert device["name"], "Device name should not be empty"

    def test_catalog_matches_database(self):
        """Verify catalog device count matches database."""
        from app import catalog
        from db import connection

        # Initialize database
        connection.initialize_database(in_memory=True)

        # Get count from database
        conn = connection.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM devices")
        db_count = cursor.fetchone()[0]

        # Load catalog
        devices = catalog.load_catalog()

        # Counts should match
        assert (
            len(devices) == db_count
        ), f"Catalog has {len(devices)} devices but database has {db_count}"

    def test_database_coverage_tables_populated(self):
        """Verify coverage calculation tables are populated."""
        from db import connection

        connection.initialize_database(in_memory=True)
        conn = connection.get_connection()
        cursor = conn.cursor()

        # Check coverage tables have data
        cursor.execute("SELECT COUNT(*) FROM wall_strobe_coverage")
        assert cursor.fetchone()[0] > 0, "wall_strobe_coverage should have data"

        cursor.execute("SELECT COUNT(*) FROM ceiling_strobe_coverage")
        assert cursor.fetchone()[0] > 0, "ceiling_strobe_coverage should have data"

        cursor.execute("SELECT COUNT(*) FROM strobe_candela")
        assert cursor.fetchone()[0] > 0, "strobe_candela should have data"

    def test_database_row_factory_set(self):
        """Verify database connection has row_factory for dict-like access."""
        import sqlite3

        from db import connection

        connection.initialize_database(in_memory=True)
        conn = connection.get_connection()

        # Check row_factory is set
        assert (
            conn.row_factory == sqlite3.Row
        ), "Connection should have row_factory set to sqlite3.Row"

        # Verify it works
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM manufacturers LIMIT 1")
        row = cursor.fetchone()

        # Should be able to access by column name
        assert "name" in row.keys()
