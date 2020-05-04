import test_base
from fixtures.files import *

import pytest
from unittest.mock import Mock,patch

from recipease.utils.parsing import *

def test_parse_num():
  test_cases = {
    "3 ": 3.0,
    "3.5": 3.5,
    "3   1/2": 3.5,
    " 3-1/2": 3.5
  }
  for t in test_cases:
    assert test_cases[t] == parse_num(t)

def test_parse_num_word():
  test_cases = {
    "an ": 1,
    " two dozen ": 24,
    " five ": 5
  }
  # TODO: "two and a half", "two and a quarter"
  for t in test_cases:
    assert test_cases[t] == parse_num_word(t)

def test_parse_ingredient():
  test_cases = {
    "about 3 cups of rice": {'qty': 3, 'unit': 'cups', 'ingredient': 'rice'},
    "3 1/2 teaspoons tomato paste": {'qty': 3.5, 'unit': 'teaspoons', 'ingredient': 'tomato paste'},
    "1 apple": {'qty': 1, 'unit': None, 'ingredient': 'apple'},
    "salt to taste": {'qty': None, 'unit': None, 'ingredient': 'salt to taste'},
    "a pinch of cumin": {'qty': 1, 'unit': 'pinch', 'ingredient': 'cumin'},
    "an egg": {'qty': 1, 'unit': None, 'ingredient': 'egg'}
  }

  with patch('recipease.utils.parsing.get_known_units') as units_mock:
    units = {'cups': 34, 'teaspoons': 16, 'teaspoon': 16, 'tsp': 16, 'pinch': 52}
    units_mock.return_value = units
    for t in test_cases:
      parsed = parse_ingredient(t)
      # won't be exact match because classes and ids are involved.
      assert test_cases[t]['qty'] == parsed['qty'] # qty should match
      if test_cases[t]['unit']:
        assert units[test_cases[t]['unit']] == parsed['unit'] # unit should be the right id
      else:
        assert parsed['unit'] is None
      assert test_cases[t]['ingredient'] == parsed['ingredient']['name'] # nested class
      assert 'Ingredient' == parsed['ingredient']['class'].__name__

# not really a unit test exactly. but this will work out all features and we can validate the whole dict.
def test_parse_recipe():
  pass
