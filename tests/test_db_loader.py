# tests/test_db_loader.py
import sqlite3
import unittest

from db import loader


class TestDbLoader(unittest.TestCase):
    def setUp(self):
        """Set up a temporary in-memory database for testing."""
        self.con = sqlite3.connect(":memory:")
        self.con.row_factory = sqlite3.Row
        loader.ensure_schema(self.con)
        from db import coverage_tables

        coverage_tables.populate_tables(self.con)

    def tearDown(self):
        """Close the database connection."""
        self.con.close()

    def test_fetch_layers(self):
        """Test that fetch_layers returns the expected default layer structure."""
        layers = loader.fetch_layers(self.con)
        self.assertIsInstance(layers, list)
        self.assertEqual(len(layers), 1)
        layer = layers[0]
        self.assertIsInstance(layer, dict)
        self.assertEqual(layer["id"], 1)
        self.assertEqual(layer["name"], "Default")
        self.assertEqual(layer["visible"], True)

    def test_fetch_devices_empty_db(self):
        """Test fetch_devices with an empty database."""
        devices = loader.fetch_devices(self.con)
        self.assertIsInstance(devices, list)
        self.assertEqual(len(devices), 0)

    def test_strobe_radius_for_candela(self):
        """Test strobe radius lookup."""
        # Populate the coverage tables
        from db import coverage_tables

        coverage_tables.populate_tables(self.con)

        # Should return None for unknown candela
        self.assertIsNone(loader.strobe_radius_for_candela(self.con, 999))

        # Test known values
        self.assertEqual(loader.strobe_radius_for_candela(self.con, 15), 15.0)
        self.assertEqual(loader.strobe_radius_for_candela(self.con, 30), 20.0)
        self.assertEqual(loader.strobe_radius_for_candela(self.con, 75), 30.0)


if __name__ == "__main__":
    unittest.main()
