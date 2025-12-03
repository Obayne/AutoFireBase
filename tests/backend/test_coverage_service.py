"""Tests for backend coverage_service (strobe candela calculations)."""

import sqlite3
from unittest.mock import patch

import pytest

from backend.coverage_service import (
    get_required_ceiling_strobe_candela,
    get_required_wall_strobe_candela,
)


@pytest.fixture
def mock_db_connection():
    """Create an in-memory SQLite database with test data."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    # Create wall strobe table
    cursor.execute(
        """
        CREATE TABLE wall_strobe_coverage (
            room_size INTEGER PRIMARY KEY,
            candela INTEGER NOT NULL
        )
    """
    )

    # Create ceiling strobe table
    cursor.execute(
        """
        CREATE TABLE ceiling_strobe_coverage (
            ceiling_height INTEGER,
            room_size INTEGER,
            candela INTEGER NOT NULL,
            PRIMARY KEY (ceiling_height, room_size)
        )
    """
    )

    # Insert test data for wall strobes
    wall_data = [
        (20, 15),
        (30, 30),
        (40, 60),
        (50, 95),
        (60, 135),
        (70, 185),
    ]
    cursor.executemany("INSERT INTO wall_strobe_coverage VALUES (?, ?)", wall_data)

    # Insert test data for ceiling strobes
    ceiling_data = [
        (10, 24, 15),
        (10, 40, 30),
        (10, 54, 60),
        (10, 70, 95),
        (10, 80, 115),
        (20, 20, 15),
        (20, 30, 30),
        (20, 40, 60),
        (20, 50, 95),
        (20, 60, 115),
        (30, 15, 15),
        (30, 25, 30),
        (30, 35, 60),
        (30, 45, 95),
        (30, 55, 115),
    ]
    cursor.executemany("INSERT INTO ceiling_strobe_coverage VALUES (?, ?, ?)", ceiling_data)

    conn.commit()
    yield conn
    conn.close()


class TestWallStrobeCandela:
    """Test wall strobe candela calculations."""

    def test_exact_match(self, mock_db_connection):
        """Test finding candela for exact room size match."""
        with patch("backend.coverage_service.get_connection", return_value=mock_db_connection):
            result = get_required_wall_strobe_candela(30)
            assert result == 30

    def test_rounds_up_to_next_size(self, mock_db_connection):
        """Test that a room size between table values rounds up."""
        with patch("backend.coverage_service.get_connection", return_value=mock_db_connection):
            # 25 is between 20 and 30, should return candela for 30
            result = get_required_wall_strobe_candela(25)
            assert result == 30

    def test_smallest_room_size(self, mock_db_connection):
        """Test smallest room size in table."""
        with patch("backend.coverage_service.get_connection", return_value=mock_db_connection):
            result = get_required_wall_strobe_candela(20)
            assert result == 15

    def test_largest_room_size(self, mock_db_connection):
        """Test largest room size in table."""
        with patch("backend.coverage_service.get_connection", return_value=mock_db_connection):
            result = get_required_wall_strobe_candela(70)
            assert result == 185

    def test_room_smaller_than_table(self, mock_db_connection):
        """Test room size smaller than smallest table entry."""
        with patch("backend.coverage_service.get_connection", return_value=mock_db_connection):
            # 10 < 20 (smallest in table), should return candela for 20
            result = get_required_wall_strobe_candela(10)
            assert result == 15

    def test_room_larger_than_table(self, mock_db_connection):
        """Test room size larger than largest table entry returns None."""
        with patch("backend.coverage_service.get_connection", return_value=mock_db_connection):
            # 100 > 70 (largest in table), should return None
            result = get_required_wall_strobe_candela(100)
            assert result is None


class TestCeilingStrobeCandela:
    """Test ceiling strobe candela calculations."""

    def test_exact_match(self, mock_db_connection):
        """Test finding candela for exact ceiling height and room size match."""
        with patch("backend.coverage_service.get_connection", return_value=mock_db_connection):
            result = get_required_ceiling_strobe_candela(ceiling_height=20, room_size=30)
            assert result == 30

    def test_rounds_up_ceiling_and_room(self, mock_db_connection):
        """Test that ceiling height and room size round up to next available."""
        with patch("backend.coverage_service.get_connection", return_value=mock_db_connection):
            # ceiling_height=15 (between 10 and 20), room_size=35 (between 30 and 40)
            # Should return entry for ceiling=20, room=40
            result = get_required_ceiling_strobe_candela(ceiling_height=15, room_size=35)
            assert result == 60

    def test_10ft_ceiling_small_room(self, mock_db_connection):
        """Test 10ft ceiling with small room."""
        with patch("backend.coverage_service.get_connection", return_value=mock_db_connection):
            result = get_required_ceiling_strobe_candela(ceiling_height=10, room_size=24)
            assert result == 15

    def test_10ft_ceiling_large_room(self, mock_db_connection):
        """Test 10ft ceiling with large room."""
        with patch("backend.coverage_service.get_connection", return_value=mock_db_connection):
            result = get_required_ceiling_strobe_candela(ceiling_height=10, room_size=70)
            assert result == 95

    def test_30ft_ceiling_small_room(self, mock_db_connection):
        """Test 30ft ceiling with small room."""
        with patch("backend.coverage_service.get_connection", return_value=mock_db_connection):
            result = get_required_ceiling_strobe_candela(ceiling_height=30, room_size=15)
            assert result == 15

    def test_30ft_ceiling_large_room(self, mock_db_connection):
        """Test 30ft ceiling with large room."""
        with patch("backend.coverage_service.get_connection", return_value=mock_db_connection):
            result = get_required_ceiling_strobe_candela(ceiling_height=30, room_size=55)
            assert result == 115

    def test_ceiling_below_table_minimum(self, mock_db_connection):
        """Test ceiling height below table minimum."""
        with patch("backend.coverage_service.get_connection", return_value=mock_db_connection):
            # ceiling=5 < 10 (min), room=30, should return entry for ceiling=10, room=40
            result = get_required_ceiling_strobe_candela(ceiling_height=5, room_size=30)
            assert result == 30

    def test_room_below_table_minimum(self, mock_db_connection):
        """Test room size below table minimum for given ceiling."""
        with patch("backend.coverage_service.get_connection", return_value=mock_db_connection):
            # ceiling=10, room=10 < 24 (min for ceiling=10)
            result = get_required_ceiling_strobe_candela(ceiling_height=10, room_size=10)
            assert result == 15

    def test_ceiling_above_table_maximum(self, mock_db_connection):
        """Test ceiling height above table maximum returns None."""
        with patch("backend.coverage_service.get_connection", return_value=mock_db_connection):
            # ceiling=40 > 30 (max), should return None
            result = get_required_ceiling_strobe_candela(ceiling_height=40, room_size=30)
            assert result is None

    def test_room_above_table_maximum(self, mock_db_connection):
        """Test room size above table maximum for given ceiling returns None."""
        with patch("backend.coverage_service.get_connection", return_value=mock_db_connection):
            # ceiling=10, room=200 > any room size in table
            result = get_required_ceiling_strobe_candela(ceiling_height=10, room_size=200)
            assert result is None

    def test_both_above_maximum(self, mock_db_connection):
        """Test both ceiling and room size above table maximums returns None."""
        with patch("backend.coverage_service.get_connection", return_value=mock_db_connection):
            result = get_required_ceiling_strobe_candela(ceiling_height=50, room_size=200)
            assert result is None
