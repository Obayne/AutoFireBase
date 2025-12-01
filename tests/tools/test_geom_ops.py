"""Tests for tools.cli.geom_ops CLI module."""

import json
from unittest.mock import patch

import pytest

from backend.models import PointDTO, SegmentDTO
from tools.cli.geom_ops import GeometryOperationsCLI


class TestGeometryOperationsCLI:
    """Test GeometryOperationsCLI class."""

    @pytest.fixture
    def cli(self):
        """Create CLI instance with mocked dependencies."""
        with patch("tools.cli.geom_ops.OpsService") as mock_ops_service:
            cli = GeometryOperationsCLI()
            cli.ops_service = mock_ops_service()
            return cli

    def test_cli_initialization(self):
        """Test that CLI initializes correctly."""
        with patch("tools.cli.geom_ops.OpsService"):
            cli = GeometryOperationsCLI()
            assert cli is not None

    def test_trim_operation_success(self, cli):
        """Test successful trim operation."""
        # Mock the trim operation
        mock_result = SegmentDTO(a=PointDTO(0, 0), b=PointDTO(5, 5))
        cli.ops_service.trim.return_value = mock_result

        # Execute trim
        result = cli.trim(segment_id="seg1", trim_point=PointDTO(2.5, 2.5), keep_start=True)

        # Verify
        assert result == mock_result
        cli.ops_service.trim.assert_called_once()

    def test_trim_operation_invalid_segment(self, cli):
        """Test trim with invalid segment ID."""
        cli.ops_service.trim.side_effect = ValueError("Segment not found")

        with pytest.raises(ValueError, match="Segment not found"):
            cli.trim(segment_id="invalid", trim_point=PointDTO(0, 0), keep_start=True)

    def test_extend_operation_success(self, cli):
        """Test successful extend operation."""
        mock_result = SegmentDTO(a=PointDTO(0, 0), b=PointDTO(15, 15))
        cli.ops_service.extend.return_value = mock_result

        result = cli.extend(segment_id="seg1", length=5.0, extend_start=False)

        assert result == mock_result
        cli.ops_service.extend.assert_called_once()

    def test_extend_negative_length(self, cli):
        """Test extend with negative length."""
        cli.ops_service.extend.side_effect = ValueError("Length must be positive")

        with pytest.raises(ValueError, match="Length must be positive"):
            cli.extend(segment_id="seg1", length=-5.0, extend_start=False)

    def test_intersect_segments_success(self, cli):
        """Test successful intersection of two segments."""
        mock_point = PointDTO(5, 5)
        cli.ops_service.intersect_segments.return_value = mock_point

        result = cli.intersect_segments(segment1_id="seg1", segment2_id="seg2")

        assert result == mock_point
        cli.ops_service.intersect_segments.assert_called_once()

    def test_intersect_parallel_segments(self, cli):
        """Test intersection of parallel segments (no intersection)."""
        cli.ops_service.intersect_segments.return_value = None

        result = cli.intersect_segments(segment1_id="seg1", segment2_id="seg2")

        assert result is None

    def test_intersect_segment_circle_success(self, cli):
        """Test successful segment-circle intersection."""
        mock_points = [PointDTO(3, 4), PointDTO(4, 3)]
        cli.ops_service.intersect_segment_circle.return_value = mock_points

        result = cli.intersect_segment_circle(segment_id="seg1", circle_id="circ1")

        assert len(result) == 2
        assert all(isinstance(p, PointDTO) for p in result)


class TestCLIInputParsing:
    """Test CLI input parsing and validation."""

    @pytest.fixture
    def cli(self):
        """Create CLI instance."""
        with patch("tools.cli.geom_ops.OpsService"):
            return GeometryOperationsCLI()

    def test_parse_point_from_string(self, cli):
        """Test parsing point from string input."""
        point_str = "10.5,20.3"
        point = cli.parse_point(point_str)

        assert isinstance(point, PointDTO)
        assert point.x == 10.5
        assert point.y == 20.3

    def test_parse_point_invalid_format(self, cli):
        """Test parsing invalid point string."""
        with pytest.raises(ValueError):
            cli.parse_point("invalid")

    def test_parse_boolean_flags(self, cli):
        """Test parsing boolean flags from CLI args."""
        assert cli.parse_bool("true") is True
        assert cli.parse_bool("True") is True
        assert cli.parse_bool("1") is True
        assert cli.parse_bool("false") is False
        assert cli.parse_bool("False") is False
        assert cli.parse_bool("0") is False


class TestCLIOutputFormatting:
    """Test CLI output formatting."""

    @pytest.fixture
    def cli(self):
        """Create CLI instance."""
        with patch("tools.cli.geom_ops.OpsService"):
            return GeometryOperationsCLI()

    def test_format_point_output(self, cli):
        """Test formatting point for display."""
        point = PointDTO(x=10.5, y=20.3)
        output = cli.format_point(point)

        assert "10.5" in output
        assert "20.3" in output

    def test_format_segment_output(self, cli):
        """Test formatting segment for display."""
        segment = SegmentDTO(a=PointDTO(0, 0), b=PointDTO(10, 10))
        output = cli.format_segment(segment)

        assert "0" in output and "10" in output

    def test_format_json_output(self, cli):
        """Test formatting results as JSON."""
        point = PointDTO(x=5.0, y=5.0)
        json_str = cli.to_json(point)

        data = json.loads(json_str)
        assert data["x"] == 5.0
        assert data["y"] == 5.0


class TestCLICommandLine:
    """Test command-line interface integration."""

    @pytest.fixture
    def cli(self):
        """Create CLI instance."""
        with patch("tools.cli.geom_ops.OpsService"):
            return GeometryOperationsCLI()

    def test_help_command(self, cli, capsys):
        """Test displaying help message."""
        cli.show_help()
        captured = capsys.readouterr()

        assert "trim" in captured.out.lower()
        assert "extend" in captured.out.lower()
        assert "intersect" in captured.out.lower()

    def test_version_command(self, cli, capsys):
        """Test displaying version."""
        cli.show_version()
        captured = capsys.readouterr()

        # Should contain version number
        assert any(c.isdigit() for c in captured.out)

    def test_list_operations_command(self, cli, capsys):
        """Test listing available operations."""
        cli.list_operations()
        captured = capsys.readouterr()

        assert "trim" in captured.out.lower()
        assert "extend" in captured.out.lower()


class TestCLIErrorHandling:
    """Test error handling in CLI."""

    @pytest.fixture
    def cli(self):
        """Create CLI instance."""
        with patch("tools.cli.geom_ops.OpsService"):
            return GeometryOperationsCLI()

    def test_missing_required_argument(self, cli):
        """Test error when required argument is missing."""
        with pytest.raises((TypeError, ValueError)):
            cli.trim(segment_id=None, trim_point=PointDTO(0, 0), keep_start=True)

    def test_invalid_geometry_reference(self, cli):
        """Test error when geometry ID doesn't exist."""
        cli.ops_service.trim.side_effect = KeyError("Geometry not found")

        with pytest.raises(KeyError):
            cli.trim(segment_id="nonexistent", trim_point=PointDTO(0, 0), keep_start=True)

    def test_operation_failure_handling(self, cli, capsys):
        """Test graceful handling of operation failures."""
        cli.ops_service.trim.side_effect = RuntimeError("Operation failed")

        try:
            cli.trim_with_error_handling(
                segment_id="seg1", trim_point=PointDTO(0, 0), keep_start=True
            )
        except RuntimeError:
            pass

        captured = capsys.readouterr()
        # Should log or display error message
        assert len(captured.err) > 0 or len(captured.out) > 0


class TestCLIBatchOperations:
    """Test batch operation capabilities."""

    @pytest.fixture
    def cli(self):
        """Create CLI instance."""
        with patch("tools.cli.geom_ops.OpsService"):
            return GeometryOperationsCLI()

    def test_batch_trim_operations(self, cli):
        """Test executing multiple trim operations."""
        operations = [
            {"segment_id": "seg1", "trim_point": PointDTO(1, 1), "keep_start": True},
            {"segment_id": "seg2", "trim_point": PointDTO(2, 2), "keep_start": False},
        ]

        cli.ops_service.trim.return_value = SegmentDTO(a=PointDTO(0, 0), b=PointDTO(5, 5))

        results = cli.batch_trim(operations)

        assert len(results) == 2
        assert cli.ops_service.trim.call_count == 2

    def test_batch_operations_from_file(self, cli, tmp_path):
        """Test loading and executing batch operations from file."""
        # Create batch file
        batch_file = tmp_path / "operations.json"
        batch_data = {
            "operations": [
                {
                    "type": "trim",
                    "segment_id": "seg1",
                    "trim_point": {"x": 5, "y": 5},
                    "keep_start": True,
                }
            ]
        }
        batch_file.write_text(json.dumps(batch_data))

        cli.ops_service.trim.return_value = SegmentDTO(a=PointDTO(0, 0), b=PointDTO(5, 5))

        # Execute batch
        results = cli.execute_batch_file(str(batch_file))

        assert len(results) == 1


class TestIntegration:
    """Integration tests for CLI operations."""

    @pytest.fixture
    def cli_with_real_service(self):
        """Create CLI with real OpsService (if available)."""
        try:
            cli = GeometryOperationsCLI()
            return cli
        except Exception:
            pytest.skip("Real OpsService not available")

    def test_full_workflow_trim_extend(self, cli_with_real_service):
        """Test a complete workflow: create, trim, extend."""
        # This test would require real geometry setup
        # Placeholder for integration test structure
        _ = cli_with_real_service  # Reserved for future implementation
        pass
