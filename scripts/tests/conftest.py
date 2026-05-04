import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"


def load_script_module(filename: str, module_name: str):
    module_path = SCRIPTS_DIR / filename
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def card_check():
    return load_script_module("card-check.py", "card_check")


@pytest.fixture
def gen_ref_docs():
    return load_script_module("generate-ref-docs.py", "generate_ref_docs")


@pytest.fixture
def gen_shared_types():
    return load_script_module("generate-shared-types.py", "generate_shared_types")
