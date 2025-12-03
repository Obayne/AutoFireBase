"""Tests for backend catalog_store (device catalog management)."""

import sqlite3
from unittest.mock import patch

import pytest

from backend.catalog_store import (
    add_device,
    get_catalog_path,
    get_device_specs,
    list_devices,
    seed_defaults,
)


@pytest.fixture
def temp_catalog_db(tmp_path):
    """Create a temporary catalog database for testing."""
    db_path = tmp_path / "test_catalog.db"

    # Mock get_catalog_path to return our temp path
    with patch("backend.catalog_store.get_catalog_path", return_value=str(db_path)):
        # Initialize schema
        from db import loader as db_loader

        con = sqlite3.connect(str(db_path))
        con.row_factory = sqlite3.Row
        db_loader.ensure_schema(con)
        con.close()

        yield str(db_path)


class TestGetCatalogPath:
    """Test get_catalog_path function."""

    def test_creates_autofire_directory(self, tmp_path):
        """Test that catalog path creates AutoFire directory in home."""
        with patch("backend.catalog_store.os.path.expanduser", return_value=str(tmp_path)):
            path = get_catalog_path()

            expected_dir = tmp_path / "AutoFire"
            assert expected_dir.exists()
            assert path == str(expected_dir / "catalog.db")

    def test_returns_string_path(self, tmp_path):
        """Test that get_catalog_path returns a string."""
        with patch("backend.catalog_store.Path.home", return_value=tmp_path):
            path = get_catalog_path()
            assert isinstance(path, str)
            assert path.endswith("catalog.db")


class TestSeedDefaults:
    """Test seed_defaults function."""

    def test_seeds_device_types(self, temp_catalog_db):
        """Test that seed_defaults creates device types."""
        with patch("backend.catalog_store.get_catalog_path", return_value=temp_catalog_db):
            seed_defaults()

            con = sqlite3.connect(temp_catalog_db)
            cur = con.cursor()
            cur.execute("SELECT code, description FROM device_types ORDER BY code")
            types = cur.fetchall()
            con.close()

            assert len(types) >= 5
            codes = [t[0] for t in types]
            assert "strobe" in codes
            assert "speaker" in codes
            assert "smoke" in codes
            assert "pull" in codes
            assert "panel" in codes

    def test_seeds_generic_manufacturer(self, temp_catalog_db):
        """Test that seed_defaults creates Generic manufacturer."""
        with patch("backend.catalog_store.get_catalog_path", return_value=temp_catalog_db):
            seed_defaults()

            con = sqlite3.connect(temp_catalog_db)
            cur = con.cursor()
            cur.execute("SELECT name FROM manufacturers WHERE name='Generic'")
            result = cur.fetchone()
            con.close()

            assert result is not None
            assert result[0] == "Generic"

    def test_idempotent_seeding(self, temp_catalog_db):
        """Test that seed_defaults can be called multiple times safely."""
        with patch("backend.catalog_store.get_catalog_path", return_value=temp_catalog_db):
            seed_defaults()
            seed_defaults()  # Second call should not duplicate

            con = sqlite3.connect(temp_catalog_db)
            cur = con.cursor()
            cur.execute("SELECT COUNT(*) FROM manufacturers WHERE name='Generic'")
            count = cur.fetchone()[0]
            con.close()

            assert count == 1  # Should only have one Generic manufacturer


class TestAddDevice:
    """Test add_device function."""

    def test_add_basic_device(self, temp_catalog_db):
        """Test adding a basic device without specs."""
        with patch("backend.catalog_store.get_catalog_path", return_value=temp_catalog_db):
            seed_defaults()  # Need device types first

            device_id = add_device(
                manufacturer="TestCorp",
                type_code="strobe",
                model="TEST-100",
                name="Test Strobe",
                symbol="TS",
            )

            assert device_id > 0

    def test_add_device_with_specs(self, temp_catalog_db):
        """Test adding a device with specifications."""
        with patch("backend.catalog_store.get_catalog_path", return_value=temp_catalog_db):
            seed_defaults()

            specs = {
                "strobe_candela": 75,
                "current_a": 0.115,
                "voltage_v": 24,
                "notes": "Test device",
            }

            device_id = add_device(
                manufacturer="TestCorp",
                type_code="strobe",
                model="TEST-200",
                name="Test Strobe with Specs",
                symbol="TSS",
                specs=specs,
            )

            assert device_id > 0

            # Verify specs were saved
            retrieved_specs = get_device_specs(device_id)
            assert retrieved_specs is not None
            assert retrieved_specs["strobe_candela"] == 75
            assert retrieved_specs["current_a"] == 0.115
            assert retrieved_specs["voltage_v"] == 24

    def test_add_device_creates_manufacturer(self, temp_catalog_db):
        """Test that add_device creates manufacturer if it doesn't exist."""
        with patch("backend.catalog_store.get_catalog_path", return_value=temp_catalog_db):
            seed_defaults()

            add_device(
                manufacturer="NewCorp", type_code="speaker", model="NEW-100", name="New Speaker"
            )

            con = sqlite3.connect(temp_catalog_db)
            cur = con.cursor()
            cur.execute("SELECT name FROM manufacturers WHERE name='NewCorp'")
            result = cur.fetchone()
            con.close()

            assert result is not None

    def test_add_device_invalid_type_code(self, temp_catalog_db):
        """Test that add_device raises ValueError for invalid type code."""
        with patch("backend.catalog_store.get_catalog_path", return_value=temp_catalog_db):
            seed_defaults()

            with pytest.raises(ValueError, match="Unknown device type code"):
                add_device(
                    manufacturer="TestCorp",
                    type_code="invalid_type",
                    model="TEST-999",
                    name="Invalid Device",
                )


class TestListDevices:
    """Test list_devices function."""

    def test_list_all_devices(self, temp_catalog_db):
        """Test listing all devices without filter."""
        with patch("backend.catalog_store.get_catalog_path", return_value=temp_catalog_db):
            seed_defaults()
            add_device("Corp1", "strobe", "M1", "Device 1")
            add_device("Corp2", "speaker", "M2", "Device 2")

            devices = list_devices()

            assert len(devices) >= 2
            assert all(isinstance(d, dict) for d in devices)
            assert all("manufacturer" in d for d in devices)
            assert all("model" in d for d in devices)

    def test_list_devices_by_type(self, temp_catalog_db):
        """Test listing devices filtered by type code."""
        with patch("backend.catalog_store.get_catalog_path", return_value=temp_catalog_db):
            seed_defaults()
            add_device("Corp1", "strobe", "M1", "Strobe 1")
            add_device("Corp2", "speaker", "M2", "Speaker 1")
            add_device("Corp3", "strobe", "M3", "Strobe 2")

            strobes = list_devices(type_code="strobe")

            assert len(strobes) == 2
            assert all(d["type"] == "strobe" for d in strobes)

    def test_list_devices_empty(self, temp_catalog_db):
        """Test listing devices when catalog is empty."""
        with patch("backend.catalog_store.get_catalog_path", return_value=temp_catalog_db):
            seed_defaults()  # Only seeds types and manufacturer, no devices

            devices = list_devices()

            assert isinstance(devices, list)
            assert len(devices) == 0

    def test_list_devices_includes_symbol(self, temp_catalog_db):
        """Test that list_devices includes symbol field."""
        with patch("backend.catalog_store.get_catalog_path", return_value=temp_catalog_db):
            seed_defaults()
            add_device("Corp", "strobe", "M1", "Device", symbol="SYM")

            devices = list_devices()

            assert len(devices) > 0
            assert "symbol" in devices[0]


class TestGetDeviceSpecs:
    """Test get_device_specs function."""

    def test_get_existing_specs(self, temp_catalog_db):
        """Test retrieving specs for a device that has them."""
        with patch("backend.catalog_store.get_catalog_path", return_value=temp_catalog_db):
            seed_defaults()

            specs = {
                "strobe_candela": 95,
                "speaker_db_at10ft": 85,
                "smoke_spacing_ft": 30,
                "current_a": 0.15,
                "voltage_v": 24,
                "notes": "Full specs",
            }

            device_id = add_device("TestCorp", "strobe", "FULL", "Full Specs Device", specs=specs)

            retrieved = get_device_specs(device_id)

            assert retrieved is not None
            assert retrieved["strobe_candela"] == 95
            assert retrieved["speaker_db_at10ft"] == 85
            assert retrieved["smoke_spacing_ft"] == 30
            assert retrieved["notes"] == "Full specs"

    def test_get_nonexistent_specs(self, temp_catalog_db):
        """Test retrieving specs for a device that has no specs."""
        with patch("backend.catalog_store.get_catalog_path", return_value=temp_catalog_db):
            seed_defaults()

            device_id = add_device("Corp", "strobe", "M1", "No Specs Device")

            specs = get_device_specs(device_id)

            assert specs is None

    def test_get_specs_invalid_device_id(self, temp_catalog_db):
        """Test retrieving specs for non-existent device ID."""
        with patch("backend.catalog_store.get_catalog_path", return_value=temp_catalog_db):
            seed_defaults()

            specs = get_device_specs(99999)

            assert specs is None

    def test_get_specs_partial_data(self, temp_catalog_db):
        """Test retrieving specs with only some fields populated."""
        with patch("backend.catalog_store.get_catalog_path", return_value=temp_catalog_db):
            seed_defaults()

            specs = {"strobe_candela": 30, "voltage_v": 12}
            device_id = add_device("Corp", "strobe", "M1", "Partial", specs=specs)

            retrieved = get_device_specs(device_id)

            assert retrieved is not None
            assert retrieved["strobe_candela"] == 30
            assert retrieved["voltage_v"] == 12
            # Other fields should be None or present but null
