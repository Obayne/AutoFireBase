# tests/test_coverage_service.py
import unittest

from backend.coverage_service import (
    get_required_ceiling_strobe_candela,
    get_required_wall_strobe_candela,
)
from db import connection


class TestCoverageService(unittest.TestCase):
    def setUp(self):
        """Set up a temporary in-memory database for testing."""
        connection.initialize_database(in_memory=True)

    def tearDown(self):
        """Close the database connection."""
        connection.close_connection()

    def test_get_required_wall_strobe_candela(self):
        """Test wall-mounted strobe candela requirements."""
        # Exact match
        self.assertEqual(get_required_wall_strobe_candela(20), 15)
        # Intermediate value, should round up
        self.assertEqual(get_required_wall_strobe_candela(21), 30)
        # Smallest value
        self.assertEqual(get_required_wall_strobe_candela(1), 15)
        # Largest value
        self.assertEqual(get_required_wall_strobe_candela(70), 185)
        # Above largest value
        self.assertIsNone(get_required_wall_strobe_candela(71))

    def test_get_required_ceiling_strobe_candela(self):
        """Test ceiling-mounted strobe candela requirements."""
        # Exact match
        self.assertEqual(get_required_ceiling_strobe_candela(10, 24), 15)
        # Intermediate room size, should round up
        self.assertEqual(get_required_ceiling_strobe_candela(10, 25), 30)
        # Intermediate ceiling height, should round up
        self.assertEqual(get_required_ceiling_strobe_candela(11, 20), 15)
        # Both intermediate
        self.assertEqual(get_required_ceiling_strobe_candela(11, 21), 30)
        # Smallest values
        self.assertEqual(get_required_ceiling_strobe_candela(1, 1), 15)
        # Out of bounds (ceiling height too high)
        self.assertIsNone(get_required_ceiling_strobe_candela(31, 15))
        # Out of bounds (room size too large for highest ceiling)
        self.assertIsNone(get_required_ceiling_strobe_candela(30, 66))


if __name__ == "__main__":
    unittest.main()
