from pathlib import Path

from backend.loader import Project, Element, save, load, save_to_path, SCHEMA_VERSION


def test_save_and_load_roundtrip_string():
    proj = Project(name="Demo", units="ft", elements=[Element(type="line", data={"a": [0, 0], "b": [10, 0]})])
    text = save(proj)
    out = load(text)
    assert out["version"] == SCHEMA_VERSION
    assert out["name"] == "Demo"
    assert out["units"] == "ft"
    assert isinstance(out.get("elements"), list) and len(out["elements"]) == 1


def test_save_and_load_roundtrip_path(tmp_path: Path):
    proj = Project(name="P", units="ft")
    p = tmp_path / "t.autofire"
    save_to_path(p, proj)
    out = load(p)
    assert out["name"] == "P"
    assert out["version"] == SCHEMA_VERSION

