import test_base
from recipease.utils.web import get_recipe
from unittest.mock import Mock,patch

import pytest

@pytest.fixture
def sample_recipe_html():
  with open('../test/fixtures/sample.html', 'r') as f:
    yield f.read()

def test_get_recipe(sample_recipe_html):
  with patch('requests.get') as get_patch:
    get_patch.return_value.text = sample_recipe_html
    url = "https://preppykitchen.com/moist-vanilla-cupcake-recipe/"
    recipe_card = get_recipe(url)
    assert recipe_card is not None
    assert recipe_card['@type'] == 'Recipe'
