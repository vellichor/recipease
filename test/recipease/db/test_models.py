import test_base
import pytest

from recipease.db.models import *

def test_unit():
  tbsp = Unit(name='tablespoon', shortname='tbsp')
  assert 'tbsp' == tbsp.get_shortname()
  assert 'tablespoon' == tbsp.get_singular()
  assert 'tablespoons' == tbsp.get_plural()

  dash = Unit(name='dash')
  assert 'dash' == dash.get_shortname()
  assert 'dash' == dash.get_singular()
  assert 'dashes' == dash.get_plural()

  assert "3 dashes" == dash.get_qty(3) # whole number
  assert "1 1/8 tablespoons" == tbsp.get_qty(1.12) # approximation
  assert "1/4 tablespoon" == tbsp.get_qty(.25) # < 1

