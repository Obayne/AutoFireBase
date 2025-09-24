from backend.schema_version import CURRENT_VERSION, get_version, is_compatible


def test_get_version_matches_constant():
    assert get_version() == CURRENT_VERSION


def test_is_compatible_same_version_true():
    assert is_compatible(CURRENT_VERSION)


def test_is_compatible_major_mismatch_false():
    assert not is_compatible("1.0.0")


def test_is_compatible_minor_bump_true():
    # Same major version considered compatible
    major = CURRENT_VERSION.split(".")[0]
    assert is_compatible(f"{major}.99.0")

