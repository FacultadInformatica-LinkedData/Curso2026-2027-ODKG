import io
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


# Smallest valid PNG (1x1 pixel)
PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
    b"\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)


@pytest.fixture()
def png():
    return io.BytesIO(PNG)
