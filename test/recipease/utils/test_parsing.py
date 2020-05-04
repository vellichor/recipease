import test_base # must go first to set the path for the rest of the app
from pprint import PrettyPrinter
import isodate

from recipease.utils.parsing import *
from fixtures.files import *

import pytest
from unittest.mock import Mock,patch

# grab isodate's favorite timezone here so we have it
tz_utc = isodate.parse_datetime('2015-03-24T00:00:00+00:00').tzinfo

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

### ISO8601 magic

# get a datetime from datetime OR date
def test_parse_datetime():
  # works on a date
  assert parse_datetime("2016-03-22") == datetime(2016, 3, 22, 0, 0, 0)
  # works on a datetime
  assert parse_datetime("2016-03-22T10:19:23+00:00") == datetime(2016, 3, 22, 10, 19, 23, tzinfo=tz_utc)
  # clean failure on garbage
  assert parse_datetime("nope") is None

# durations to minutes
def test_duration_to_minutes():
  assert 20 == duration_to_minutes("PT20M")
  assert 2 == duration_to_minutes("PT120S")
  assert 1441 == duration_to_minutes("P1DT1M")

def test_minutes_to_duration():
  assert "PT1H30M" == minutes_to_duration(90)
  assert "P1DT30M" == minutes_to_duration(1470)

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
def test_parse_recipe(sample_recipe_json):
  with patch('recipease.utils.parsing.get_known_units') as units_mock:
    units = {'cups': 34, 'cup': 34, 'teaspoons': 16, 'teaspoon': 16, 'tsp': 16, 'pinch': 52}
    units_mock.return_value = units
    recipe_dict = parse_recipe(sample_recipe_json)
    # literal keys
    assert "Moist Vanilla Cupcakes" == recipe_dict['name']
    assert "Dessert" == recipe_dict['category']
    assert 20 == recipe_dict['cook_time']
    assert 15 == recipe_dict['prep_time']
    assert "American" == recipe_dict['cuisine']
    assert datetime(2019, 8, 25, 0, 0, 57, tzinfo=tz_utc) \
            == recipe_dict['date_published']
    assert recipe_dict['description'].startswith("A simple vanilla cupcake")
    # images should be an ImageSet with 4 members
    assert recipe_dict['images']['class'].__name__ == 'ImageSet'
    assert 4 == len(recipe_dict['images']['images'])
    # there are n ingredients
    # we already tested ingredient parsing so don't worry about contents
    assert 16 == len(recipe_dict['ingredients'])
    # STEPS. there should be two sections
    assert 2 == len(recipe_dict['steps'])
    assert recipe_dict['steps'][1]['class'].__name__ == 'Section'
    # First section: validate name and class
    section0 = recipe_dict['steps'][0]
    assert section0['class'].__name__ == 'Section'
    assert section0['name'] == "For the Cupcakes:"
    # should have 7 steps, validate first and last
    assert 7 == len(section0['steps'])
    assert section0['steps'][0]['class'].__name__ == 'Step'
    assert section0['steps'][0]['text'].startswith("Preheat oven")
    assert section0['steps'][6]['class'].__name__ == 'Step'
    assert section0['steps'][6]['text'].startswith("Bake for about 18 minutes")
    # second section should be same same, just check type and length
    section1 = recipe_dict['steps'][1]
    assert section1['class'].__name__ == 'Section'
    assert 3 == len(section1['steps'])







