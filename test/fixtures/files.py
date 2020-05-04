import json
import pytest

@pytest.fixture
def sample_recipe_html():
  with open('../test/fixtures/static/sample.html', 'r') as f:
    yield f.read()

@pytest.fixture
def sample_recipe_json():
  with open('../test/fixtures/static/sample2.json', 'r') as f:
    yield json.loads(f.read())
