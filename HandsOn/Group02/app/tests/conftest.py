import sys
from pathlib import Path

import pytest

APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))

from app import create_app  # noqa: E402


@pytest.fixture(scope="session")
def app(tmp_path_factory):
    data_dir = tmp_path_factory.mktemp("data")
    return create_app({"TESTING": True, "DATA_DIR": str(data_dir), "WIKIDATA_ENABLED": False})


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture(scope="session")
def services(app):
    return app.extensions["explorer"]

