import pytest

@pytest.fixture
def sample_recipe_html():
  with open('../test/fixtures/static/sample.html', 'r') as f:
    yield f.read()
