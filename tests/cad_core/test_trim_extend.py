"""Tests for enhanced trim/extend operations."""

import pytest
import math

from cad_core.lines import Point, Line
from cad_core.trim_extend import (
    TrimResult,
    ExtendResult,
    FilletResult,
    Arc,
    trim_line_to_boundary,
    extend_line_to_boundary,
    trim_multiple_lines,
    extend_multiple_lines,
    break_line_at_points,
    find_line_line_intersections,
    fillet_two_lines,
    fillet_multiple_line_pairs,
    distance_point_to_point,
)


class TestBasicOperations:
    """Test basic trim and extend operations."""
    
    def test_distance_point_to_point(self):
        """Test distance calculation between points."""
        p1 = Point(0, 0)
        p2 = Point(3, 4)
        assert abs(distance_point_to_point(p1, p2) - 5.0) < 1e-9
    
    def test_find_line_line_intersections_infinite(self):
        """Test finding intersections between infinite lines."""
        l1 = Line(Point(0, 0), Point(10, 0))  # Horizontal line
        l2 = Line(Point(5, -5), Point(5, 5))  # Vertical line
        
        intersections = find_line_line_intersections(l1, l2, as_infinite=True)
        assert len(intersections) == 1
        assert abs(intersections[0].x - 5.0) < 1e-9
        assert abs(intersections[0].y - 0.0) < 1e-9
    
    def test_find_line_line_intersections_segments(self):
        """Test finding intersections between line segments."""
        l1 = Line(Point(0, 0), Point(10, 0))  # Horizontal segment
        l2 = Line(Point(5, -1), Point(5, 1))  # Vertical segment crossing
        
        intersections = find_line_line_intersections(l1, l2, as_infinite=False)
        assert len(intersections) == 1
        assert abs(intersections[0].x - 5.0) < 1e-9
        assert abs(intersections[0].y - 0.0) < 1e-9
    
    def test_find_line_line_intersections_no_crossing(self):
        """Test segments that don't cross."""
        l1 = Line(Point(0, 0), Point(5, 0))   # Short horizontal segment
        l2 = Line(Point(6, -1), Point(6, 1))  # Vertical segment not crossing
        
        intersections = find_line_line_intersections(l1, l2, as_infinite=False)
        assert len(intersections) == 0
    
    def test_find_line_line_intersections_parallel(self):
        """Test parallel lines have no intersection."""
        l1 = Line(Point(0, 0), Point(10, 0))
        l2 = Line(Point(0, 1), Point(10, 1))
        
        intersections = find_line_line_intersections(l1, l2, as_infinite=True)
        assert len(intersections) == 0


class TestTrimOperations:
    """Test line trimming operations."""
    
    def test_trim_line_basic(self):
        """Test basic line trimming."""
        line = Line(Point(0, 0), Point(10, 0))     # Horizontal line
        boundary = Line(Point(5, -5), Point(5, 5)) # Vertical boundary
        
        result = trim_line_to_boundary(line, boundary, end="b")
        
        assert result.success
        assert result.trimmed_element is not None
        assert abs(result.trimmed_element.a.x - 0.0) < 1e-9
        assert abs(result.trimmed_element.a.y - 0.0) < 1e-9
        assert abs(result.trimmed_element.b.x - 5.0) < 1e-9
        assert abs(result.trimmed_element.b.y - 0.0) < 1e-9
    
    def test_trim_line_end_a(self):
        """Test trimming end 'a' of a line."""
        line = Line(Point(0, 0), Point(10, 0))
        boundary = Line(Point(3, -5), Point(3, 5))
        
        result = trim_line_to_boundary(line, boundary, end="a")
        
        assert result.success
        assert result.trimmed_element is not None
        assert abs(result.trimmed_element.a.x - 3.0) < 1e-9
        assert abs(result.trimmed_element.b.x - 10.0) < 1e-9
    
    def test_trim_line_no_intersection(self):
        """Test trimming when there's no intersection."""
        line = Line(Point(0, 0), Point(10, 0))
        boundary = Line(Point(0, 1), Point(10, 1))  # Parallel line
        
        result = trim_line_to_boundary(line, boundary, end="b")
        
        assert not result.success
        assert "No intersection found" in result.reason
    
    def test_trim_line_invalid_end(self):
        """Test trimming with invalid end parameter."""
        line = Line(Point(0, 0), Point(10, 0))
        boundary = Line(Point(5, -5), Point(5, 5))
        
        result = trim_line_to_boundary(line, boundary, end="z")
        
        assert not result.success
        assert "Invalid end parameter" in result.reason
    
    def test_trim_line_intersection_too_close(self):
        """Test trimming when intersection is too close to endpoint."""
        line = Line(Point(0, 0), Point(10, 0))
        boundary = Line(Point(10, -5), Point(10, 5))  # Boundary at endpoint
        
        result = trim_line_to_boundary(line, boundary, end="b")
        
        assert not result.success
        assert "too close to endpoint" in result.reason


class TestExtendOperations:
    """Test line extension operations."""
    
    def test_extend_line_basic(self):
        """Test basic line extension."""
        line = Line(Point(0, 0), Point(5, 0))      # Short horizontal line
        boundary = Line(Point(10, -5), Point(10, 5)) # Vertical boundary
        
        result = extend_line_to_boundary(line, boundary, end="b")
        
        assert result.success
        assert result.extended_element is not None
        assert abs(result.extended_element.a.x - 0.0) < 1e-9
        assert abs(result.extended_element.a.y - 0.0) < 1e-9
        assert abs(result.extended_element.b.x - 10.0) < 1e-9
        assert abs(result.extended_element.b.y - 0.0) < 1e-9
    
    def test_extend_line_end_a(self):
        """Test extending end 'a' of a line."""
        line = Line(Point(5, 0), Point(10, 0))
        boundary = Line(Point(0, -5), Point(0, 5))
        
        result = extend_line_to_boundary(line, boundary, end="a")
        
        assert result.success
        assert result.extended_element is not None
        assert abs(result.extended_element.a.x - 0.0) < 1e-9
        assert abs(result.extended_element.b.x - 10.0) < 1e-9
    
    def test_extend_line_no_intersection(self):
        """Test extending when there's no intersection."""
        line = Line(Point(0, 0), Point(5, 0))
        boundary = Line(Point(0, 1), Point(5, 1))  # Parallel line
        
        result = extend_line_to_boundary(line, boundary, end="b")
        
        assert not result.success
        assert "No intersection found" in result.reason
    
    def test_extend_line_wrong_direction(self):
        """Test extending when intersection is in wrong direction."""
        line = Line(Point(5, 0), Point(10, 0))
        boundary = Line(Point(0, -5), Point(0, 5))  # Boundary behind the line
        
        result = extend_line_to_boundary(line, boundary, end="b")
        
        assert not result.success
        assert "not in extension direction" in result.reason
    
    def test_extend_line_invalid_end(self):
        """Test extending with invalid end parameter."""
        line = Line(Point(0, 0), Point(5, 0))
        boundary = Line(Point(10, -5), Point(10, 5))
        
        result = extend_line_to_boundary(line, boundary, end="invalid")
        
        assert not result.success
        assert "Invalid end parameter" in result.reason


class TestMultipleOperations:
    """Test operations on multiple lines."""
    
    def test_trim_multiple_lines(self):
        """Test trimming multiple lines."""
        lines = [
            Line(Point(0, 0), Point(10, 0)),    # Horizontal line 1
            Line(Point(0, 2), Point(10, 2)),    # Horizontal line 2
            Line(Point(0, 4), Point(10, 4)),    # Horizontal line 3
        ]
        cutters = [
            Line(Point(5, -1), Point(5, 5)),    # Vertical cutter
        ]
        
        results = trim_multiple_lines(lines, cutters)
        
        assert len(results) == 3
        for result in results:
            assert result.success
            assert result.trimmed_element is not None
            # Lines should be trimmed - check that they are shorter than original
            original_length = 10.0
            trimmed_length = distance_point_to_point(
                result.trimmed_element.a, result.trimmed_element.b
            )
            assert trimmed_length < original_length
    
    def test_extend_multiple_lines(self):
        """Test extending multiple lines."""
        lines = [
            Line(Point(0, 0), Point(3, 0)),     # Short horizontal line 1
            Line(Point(0, 2), Point(3, 2)),     # Short horizontal line 2
        ]
        boundaries = [
            Line(Point(5, -1), Point(5, 3)),    # Vertical boundary
        ]
        
        results = extend_multiple_lines(lines, boundaries)
        
        assert len(results) == 2
        for result in results:
            assert result.success
            assert result.extended_element is not None
            # All lines should be extended to x=5
            assert abs(result.extended_element.b.x - 5.0) < 1e-9
    
    def test_trim_multiple_no_valid_cuts(self):
        """Test trimming when no valid cuts are possible."""
        lines = [
            Line(Point(0, 0), Point(5, 0)),     # Horizontal line
        ]
        cutters = [
            Line(Point(0, 1), Point(5, 1)),     # Parallel cutter
        ]
        
        results = trim_multiple_lines(lines, cutters)
        
        assert len(results) == 1
        assert not results[0].success
        assert "No valid cuts found" in results[0].reason


class TestBreakOperations:
    """Test line breaking operations."""
    
    def test_break_line_single_point(self):
        """Test breaking a line at a single point."""
        line = Line(Point(0, 0), Point(10, 0))
        break_points = [Point(5, 0)]
        
        segments = break_line_at_points(line, break_points)
        
        assert len(segments) == 2
        assert abs(segments[0].a.x - 0.0) < 1e-9
        assert abs(segments[0].b.x - 5.0) < 1e-9
        assert abs(segments[1].a.x - 5.0) < 1e-9
        assert abs(segments[1].b.x - 10.0) < 1e-9
    
    def test_break_line_multiple_points(self):
        """Test breaking a line at multiple points."""
        line = Line(Point(0, 0), Point(10, 0))
        break_points = [Point(3, 0), Point(7, 0), Point(5, 0)]  # Unsorted
        
        segments = break_line_at_points(line, break_points)
        
        assert len(segments) == 4
        # Should be sorted: 0->3, 3->5, 5->7, 7->10
        expected_x_coords = [(0, 3), (3, 5), (5, 7), (7, 10)]
        for i, (start_x, end_x) in enumerate(expected_x_coords):
            assert abs(segments[i].a.x - start_x) < 1e-9
            assert abs(segments[i].b.x - end_x) < 1e-9
    
    def test_break_line_no_valid_points(self):
        """Test breaking when no break points lie on the line."""
        line = Line(Point(0, 0), Point(10, 0))
        break_points = [Point(5, 1)]  # Point not on line
        
        segments = break_line_at_points(line, break_points)
        
        assert len(segments) == 1
        assert segments[0] == line
    
    def test_break_line_points_at_endpoints(self):
        """Test breaking with points at line endpoints."""
        line = Line(Point(0, 0), Point(10, 0))
        break_points = [Point(0, 0), Point(10, 0), Point(5, 0)]
        
        segments = break_line_at_points(line, break_points)
        
        # Should create segments excluding endpoint breaks, so 2 segments from the middle point
        assert len(segments) == 2
        assert abs(segments[0].a.x - 0) < 1e-9
        assert abs(segments[0].b.x - 5) < 1e-9
        assert abs(segments[1].a.x - 5) < 1e-9
        assert abs(segments[1].b.x - 10) < 1e-9
        assert abs(segments[0].a.x - 0.0) < 1e-9
        assert abs(segments[0].b.x - 5.0) < 1e-9


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_collinear_lines(self):
        """Test operations with collinear lines."""
        line1 = Line(Point(0, 0), Point(5, 0))
        line2 = Line(Point(3, 0), Point(8, 0))  # Overlapping collinear line
        
        # These operations should handle collinear cases gracefully
        trim_result = trim_line_to_boundary(line1, line2, end="b")
        extend_result = extend_line_to_boundary(line1, line2, end="b")
        
        # Both should fail since collinear lines don't have a unique intersection
        assert not trim_result.success
        assert not extend_result.success
    
    def test_zero_length_line(self):
        """Test operations with zero-length lines."""
        zero_line = Line(Point(5, 5), Point(5, 5))
        boundary = Line(Point(0, 0), Point(10, 10))
        
        result = trim_line_to_boundary(zero_line, boundary, end="b")
        # Should handle gracefully
        assert isinstance(result, TrimResult)
    
    def test_very_close_points(self):
        """Test operations with very close points."""
        line = Line(Point(0, 0), Point(1e-10, 0))  # Very short line
        boundary = Line(Point(0, -1), Point(0, 1))
        
        result = trim_line_to_boundary(line, boundary, end="b")
        # Should handle near-zero cases
        assert isinstance(result, TrimResult)


class TestFilletOperations:
    """Test fillet operations."""
    
    def test_basic_fillet_perpendicular_lines(self):
        """Test fillet of two perpendicular lines."""
        line1 = Line(Point(0, 0), Point(5, 0))
        line2 = Line(Point(5, 0), Point(5, 5))
        radius = 1.0
        
        result = fillet_two_lines(line1, line2, radius)
        
        assert result.success
        assert result.arc is not None
        assert result.trimmed_line1 is not None
        assert result.trimmed_line2 is not None
        assert abs(result.arc.radius - radius) < 1e-9
    
    def test_fillet_intersecting_lines(self):
        """Test fillet of two intersecting lines at angle."""
        line1 = Line(Point(0, 0), Point(4, 0))
        line2 = Line(Point(4, 0), Point(4, 3))
        radius = 0.5
        
        result = fillet_two_lines(line1, line2, radius)
        
        assert result.success
        assert result.arc is not None
        assert abs(result.arc.radius - radius) < 1e-9
        # Arc should connect the trimmed lines smoothly
        assert result.arc.start_point() is not None
        assert result.arc.end_point() is not None
    
    def test_fillet_parallel_lines_fails(self):
        """Test that fillet fails for parallel lines."""
        line1 = Line(Point(0, 0), Point(5, 0))
        line2 = Line(Point(0, 1), Point(5, 1))
        radius = 1.0
        
        result = fillet_two_lines(line1, line2, radius)
        
        assert not result.success
        # The error message could be either "parallel" or "do not intersect" 
        assert ("parallel" in result.reason.lower() or "intersect" in result.reason.lower())
    
    def test_fillet_invalid_radius(self):
        """Test that fillet fails for invalid radius."""
        line1 = Line(Point(0, 0), Point(5, 0))
        line2 = Line(Point(5, 0), Point(5, 5))
        
        # Test negative radius
        result = fillet_two_lines(line1, line2, -1.0)
        assert not result.success
        assert "positive" in result.reason.lower()
        
        # Test zero radius
        result = fillet_two_lines(line1, line2, 0.0)
        assert not result.success
        assert "positive" in result.reason.lower()
    
    def test_fillet_non_intersecting_lines(self):
        """Test fillet of lines that don't intersect."""
        line1 = Line(Point(0, 0), Point(2, 0))
        line2 = Line(Point(5, 1), Point(7, 1))
        radius = 1.0
        
        result = fillet_two_lines(line1, line2, radius)
        
        assert not result.success
        assert "intersect" in result.reason.lower()
    
    def test_fillet_multiple_line_pairs(self):
        """Test filleting multiple line pairs."""
        pairs = [
            (Line(Point(0, 0), Point(5, 0)), Line(Point(5, 0), Point(5, 5))),
            (Line(Point(10, 0), Point(15, 0)), Line(Point(15, 0), Point(15, 3))),
        ]
        radius = 0.5
        
        results = fillet_multiple_line_pairs(pairs, radius)
        
        assert len(results) == 2
        for result in results:
            assert result.success
            assert result.arc is not None
            assert abs(result.arc.radius - radius) < 1e-9
    
    def test_arc_start_end_points(self):
        """Test Arc start_point and end_point methods."""
        center = Point(0, 0)
        radius = 5.0
        start_angle = 0.0  # 0 degrees
        end_angle = math.pi / 2  # 90 degrees
        
        arc = Arc(center, radius, start_angle, end_angle)
        
        start_pt = arc.start_point()
        end_pt = arc.end_point()
        
        # Start point should be at (5, 0)
        assert abs(start_pt.x - 5.0) < 1e-9
        assert abs(start_pt.y - 0.0) < 1e-9
        
        # End point should be at (0, 5)
        assert abs(end_pt.x - 0.0) < 1e-9
        assert abs(end_pt.y - 5.0) < 1e-9
    
    def test_fillet_result_dataclass(self):
        """Test FilletResult dataclass functionality."""
        result = FilletResult(None, None, None, False, "Test reason")
        
        assert result.arc is None
        assert result.trimmed_line1 is None
        assert result.trimmed_line2 is None
        assert not result.success
        assert result.reason == "Test reason"
        
        # Test with actual objects
        arc = Arc(Point(0, 0), 1.0, 0.0, math.pi/2)
        line1 = Line(Point(0, 0), Point(1, 0))
        line2 = Line(Point(0, 0), Point(0, 1))
        
        result2 = FilletResult(arc, line1, line2, True, "Success")
        
        assert result2.arc == arc
        assert result2.trimmed_line1 == line1
        assert result2.trimmed_line2 == line2
        assert result2.success
        assert result2.reason == "Success"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])