# TODO: find a better way to import the app, this is cumbersome
# and only works if you run pytest from the test directory
import sys
sys.path.append('../')

import pytest
from starlette.testclient import TestClient

from fastapi_hello_world import app

@pytest.fixture
def client():
    client = TestClient(app)
    yield client

