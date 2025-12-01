"""Tests for tools.cli.communication_log module."""

import json
import tempfile
from pathlib import Path

import pytest

from tools.cli.communication_log import CommunicationLogger, LogEntry, SessionLog


class TestLogEntry:
    """Test LogEntry dataclass."""

    def test_log_entry_creation(self):
        """Test creating a log entry."""
        entry = LogEntry(
            timestamp=1234567890.0,
            operation="trim",
            input_data={"segment": "seg1"},
            output_data={"result": "success"},
            status="completed",
        )

        assert entry.timestamp == 1234567890.0
        assert entry.operation == "trim"
        assert entry.status == "completed"
        assert entry.input_data["segment"] == "seg1"


class TestSessionLog:
    """Test SessionLog dataclass."""

    def test_session_log_creation(self):
        """Test creating a session log."""
        session = SessionLog(session_id="test-session-123", start_time=1234567890.0, entries=[])

        assert session.session_id == "test-session-123"
        assert session.start_time == 1234567890.0
        assert len(session.entries) == 0

    def test_session_log_with_entries(self):
        """Test session log with multiple entries."""
        entries = [
            LogEntry(1.0, "op1", {}, {}, "completed"),
            LogEntry(2.0, "op2", {}, {}, "completed"),
        ]
        session = SessionLog("test", 0.0, entries)
        assert len(session.entries) == 2


class TestCommunicationLogger:
    """Test CommunicationLogger class."""

    @pytest.fixture
    def temp_log_dir(self):
        """Create a temporary directory for log files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def logger(self, temp_log_dir):
        """Create a logger instance with temporary directory."""
        return CommunicationLogger(log_dir=temp_log_dir)

    def test_logger_initialization(self, temp_log_dir):
        """Test that logger initializes correctly."""
        logger = CommunicationLogger(log_dir=temp_log_dir)
        assert logger.log_dir == temp_log_dir
        assert temp_log_dir.exists()

    def test_log_dir_creation(self, temp_log_dir):
        """Test that log directory is created if it doesn't exist."""
        nested_dir = temp_log_dir / "nested" / "logs"
        CommunicationLogger(log_dir=nested_dir)
        assert nested_dir.exists()

    def test_start_session(self, logger):
        """Test starting a new session."""
        session_id = logger.start_session()
        assert isinstance(session_id, str)
        assert len(session_id) > 0

    def test_log_operation(self, logger):
        """Test logging an operation."""
        session_id = logger.start_session()
        logger.log_operation(
            session_id=session_id,
            operation="test_op",
            input_data={"key": "value"},
            output_data={"result": "success"},
            status="completed",
        )

        # Verify operation was logged
        assert session_id in logger._sessions
        session = logger._sessions[session_id]
        assert len(session.entries) == 1
        assert session.entries[0].operation == "test_op"

    def test_multiple_operations_in_session(self, logger):
        """Test logging multiple operations in a single session."""
        session_id = logger.start_session()

        for i in range(5):
            logger.log_operation(
                session_id=session_id,
                operation=f"op_{i}",
                input_data={},
                output_data={},
                status="completed",
            )

        session = logger._sessions[session_id]
        assert len(session.entries) == 5

    def test_save_session_json(self, logger, temp_log_dir):
        """Test saving session to JSON file."""
        session_id = logger.start_session()
        logger.log_operation(
            session_id=session_id,
            operation="test",
            input_data={},
            output_data={},
            status="completed",
        )

        # Save session
        logger.save_session(session_id, format="json")

        # Verify file exists
        json_files = list(temp_log_dir.glob("*.json"))
        assert len(json_files) > 0

        # Verify content
        with open(json_files[0]) as f:
            data = json.load(f)
            assert data["session_id"] == session_id
            assert len(data["entries"]) == 1

    def test_save_session_markdown(self, logger, temp_log_dir):
        """Test saving session to Markdown report."""
        session_id = logger.start_session()
        logger.log_operation(
            session_id=session_id,
            operation="test",
            input_data={"input": "data"},
            output_data={"output": "result"},
            status="completed",
        )

        # Save as markdown
        logger.save_session(session_id, format="markdown")

        # Verify file exists
        md_files = list(temp_log_dir.glob("*_report.md"))
        assert len(md_files) > 0

        # Verify content contains expected sections
        content = md_files[0].read_text()
        assert "# Communication Log Report" in content
        assert session_id in content
        assert "test" in content

    def test_get_session_summary(self, logger):
        """Test getting session summary statistics."""
        session_id = logger.start_session()

        # Log operations with different statuses
        logger.log_operation(session_id, "op1", {}, {}, "completed")
        logger.log_operation(session_id, "op2", {}, {}, "completed")
        logger.log_operation(session_id, "op3", {}, {}, "failed")

        summary = logger.get_session_summary(session_id)

        assert summary["total_operations"] == 3
        assert summary["completed"] == 2
        assert summary["failed"] == 1

    def test_invalid_session_id(self, logger):
        """Test handling of invalid session ID."""
        with pytest.raises((KeyError, ValueError)):
            logger.log_operation("invalid-session", "op", {}, {}, "completed")

    def test_session_timestamps(self, logger):
        """Test that session and entry timestamps are recorded."""
        import time

        session_id = logger.start_session()
        time.sleep(0.01)  # Small delay

        logger.log_operation(session_id, "op1", {}, {}, "completed")

        session = logger._sessions[session_id]
        entry = session.entries[0]

        # Timestamps should be positive numbers
        assert session.start_time > 0
        assert entry.timestamp > 0
        assert entry.timestamp >= session.start_time


class TestLogFormats:
    """Test different log output formats."""

    @pytest.fixture
    def logger(self, tmp_path):
        """Create logger with temp directory."""
        return CommunicationLogger(log_dir=tmp_path)

    def test_json_format_structure(self, logger, tmp_path):
        """Test JSON output has correct structure."""
        session_id = logger.start_session()
        logger.log_operation(session_id, "test", {"a": 1}, {"b": 2}, "completed")
        logger.save_session(session_id, format="json")

        json_file = next(tmp_path.glob("*.json"))
        data = json.loads(json_file.read_text())

        assert "session_id" in data
        assert "start_time" in data
        assert "entries" in data
        assert isinstance(data["entries"], list)

    def test_markdown_format_readability(self, logger, tmp_path):
        """Test Markdown output is human-readable."""
        session_id = logger.start_session()
        logger.log_operation(
            session_id, "geometry_operation", {"type": "trim"}, {"success": True}, "completed"
        )
        logger.save_session(session_id, format="markdown")

        md_file = next(tmp_path.glob("*_report.md"))
        content = md_file.read_text()

        # Should contain markdown headers
        assert content.startswith("#")
        # Should contain the operation name
        assert "geometry_operation" in content
        # Should have formatting
        assert "**" in content or "##" in content
