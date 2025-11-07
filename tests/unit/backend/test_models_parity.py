from backend import models as legacy
from lv_cad.backend import models as migrated


def test_models_dataclasses_exist_and_fields():
    # Ensure dataclasses exist and have matching field names
    assert hasattr(legacy, "PointDTO")
    assert hasattr(migrated, "PointDTO")
    p_fields = tuple(f.name for f in legacy.PointDTO.__dataclass_fields__.values())
    m_fields = tuple(f.name for f in migrated.PointDTO.__dataclass_fields__.values())
    assert p_fields == m_fields

    assert hasattr(legacy, "FilletArcDTO")
    assert hasattr(migrated, "FilletArcDTO")
    lf = tuple(f.name for f in legacy.FilletArcDTO.__dataclass_fields__.values())
    mf = tuple(f.name for f in migrated.FilletArcDTO.__dataclass_fields__.values())
    assert lf == mf
