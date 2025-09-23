"""Tests for Point operations and utilities."""

import pytest
import math
from cad_core.lines import Point


class TestPointOperations:
    """Test Point class and related operations."""
    
    def test_point_creation(self):
        """Test basic point creation."""
        p = Point(3.0, 4.0)
        assert p.x == 3.0
        assert p.y == 4.0
    
    def test_point_equality(self):
        """Test point equality comparison."""
        p1 = Point(1.0, 2.0)
        p2 = Point(1.0, 2.0)
        p3 = Point(1.1, 2.0)
        
        assert p1 == p2
        assert p1 != p3
    
    def test_point_distance_calculation(self):
        """Test distance calculation between points."""
        p1 = Point(0.0, 0.0)
        p2 = Point(3.0, 4.0)
        
        # Using distance function from trim_extend module
        from cad_core.trim_extend import distance_point_to_point
        dist = distance_point_to_point(p1, p2)
        
        assert abs(dist - 5.0) < 1e-9
    
    def test_point_distance_zero(self):
        """Test distance between identical points."""
        p1 = Point(5.0, 7.0)
        p2 = Point(5.0, 7.0)
        
        from cad_core.trim_extend import distance_point_to_point
        dist = distance_point_to_point(p1, p2)
        
        assert dist < 1e-9
    
    def test_point_distance_negative_coordinates(self):
        """Test distance with negative coordinates."""
        p1 = Point(-3.0, -4.0)
        p2 = Point(0.0, 0.0)
        
        from cad_core.trim_extend import distance_point_to_point
        dist = distance_point_to_point(p1, p2)
        
        assert abs(dist - 5.0) < 1e-9
    
    def test_point_very_small_coordinates(self):
        """Test points with very small coordinates."""
        p1 = Point(1e-10, 1e-10)
        p2 = Point(2e-10, 2e-10)
        
        from cad_core.trim_extend import distance_point_to_point
        dist = distance_point_to_point(p1, p2)
        
        expected = math.sqrt(2) * 1e-10
        assert abs(dist - expected) < 1e-15
    
    def test_point_very_large_coordinates(self):
        """Test points with very large coordinates."""
        p1 = Point(1e6, 1e6)
        p2 = Point(1e6 + 3, 1e6 + 4)
        
        from cad_core.trim_extend import distance_point_to_point
        dist = distance_point_to_point(p1, p2)
        
        assert abs(dist - 5.0) < 1e-6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])