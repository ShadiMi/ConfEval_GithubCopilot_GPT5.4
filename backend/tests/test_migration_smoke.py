from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


REVISION_PATH = Path(__file__).resolve().parents[1] / "alembic" / "versions" / "20260413_0001_initial_schema.py"


def load_revision_module():
    spec = spec_from_file_location("initial_schema_revision", REVISION_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_initial_revision_metadata() -> None:
    module = load_revision_module()

    assert module.revision == "20260413_0001"
    assert module.down_revision is None
    assert callable(module.upgrade)
    assert callable(module.downgrade)
