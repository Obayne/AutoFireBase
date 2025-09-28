import tempfile
from pathlib import Path
import pytest
from scripts.tools._auto_resolve_conflicts import _split_conflict_blocks, resolve_file


def test_split_conflict_blocks_no_conflicts():
    """Test that text without conflicts is unchanged."""
    text = "line 1\nline 2\nline 3"
    changed, new_text = _split_conflict_blocks(text)
    assert not changed
    assert new_text == text


def test_split_conflict_blocks_simple_conflict():
    """Test resolving a simple conflict by keeping the stashed side."""
    text = """line 1
<<<<<<< HEAD
old content
=======
new content
>>>>>>> stash
line 2"""
    changed, new_text = _split_conflict_blocks(text)
    assert changed
    expected = "line 1\nnew content\nline 2"
    assert new_text == expected


def test_split_conflict_blocks_multiple_conflicts():
    """Test resolving multiple conflicts in one file."""
    text = """start
<<<<<<< HEAD
old1
=======
new1
>>>>>>> stash1
middle
<<<<<<< HEAD
old2
=======
new2
>>>>>>> stash2
end"""
    changed, new_text = _split_conflict_blocks(text)
    assert changed
    expected = "start\nnew1\nmiddle\nnew2\nend"
    assert new_text == expected


def test_split_conflict_blocks_malformed_missing_separator():
    """Test that malformed conflicts (missing =======) are left unchanged."""
    text = """line 1
<<<<<<< HEAD
old content
new content
>>>>>>> stash
line 2"""
    changed, new_text = _split_conflict_blocks(text)
    assert not changed
    assert new_text == text


def test_split_conflict_blocks_malformed_missing_end():
    """Test that malformed conflicts (missing >>>>>>>) are left unchanged."""
    text = """line 1
<<<<<<< HEAD
old content
=======
new content
line 2"""
    changed, new_text = _split_conflict_blocks(text)
    assert not changed
    assert new_text == text


def test_resolve_file_creates_backup():
    """Test that resolve_file creates a backup when modifying a file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test.txt"
        original_content = """line 1
<<<<<<< HEAD
old
=======
new
>>>>>>> stash
line 2"""
        path.write_text(original_content)

        result = resolve_file(path)
        assert result is True

        # Check backup was created
        backup = path.with_suffix(path.suffix + ".bak-conflict-resolve")
        assert backup.exists()
        assert backup.read_text() == original_content

        # Check file was modified
        new_content = path.read_text()
        assert "new" in new_content
        assert "<<<<<<< HEAD" not in new_content


def test_resolve_file_no_changes():
    """Test that resolve_file returns True even when no changes are made."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test.txt"
        content = "normal file content"
        path.write_text(content)

        result = resolve_file(path)
        assert result is True

        # No backup should be created
        backup = path.with_suffix(path.suffix + ".bak-conflict-resolve")
        assert not backup.exists()

        # Content should be unchanged
        assert path.read_text() == content