import test_base

from fixtures.db import empty_db_session as session
from recipease.utils.conversions import *

from sqlalchemy.orm.exc import NoResultFound

import pytest

def test_create_all(session):
  create_all_units(session)
  create_all_conversions(session)
  # didn't crash
  # see if we have the expected things
  # some units
  assert len(session.query(Unit).filter(Unit.name=='cup').all()) == 1
  assert len(session.query(Unit).filter(Unit.shortname=='pt').all()) == 1
  assert len(session.query(Unit).filter(Unit.name=='gram').all()) == 1
  # conversions
  cup = session.query(Unit).filter(Unit.name=='cup').one()
  pint = session.query(Unit).filter(Unit.name=='pint').one()
  result = session.query(Conversion).filter(Conversion.num_unit_id==cup.id and Conversion.denom_unit_id==pint.id).all()
  assert len(result) == 1
  cups_to_pints = result[0]
  assert 2.0 == cups_to_pints.num_qty / cups_to_pints.denom_qty

def test_get_unit(session):
  create_all_units(session)
  assert get_unit('smidgen', session).name == 'smidgen'
  assert get_unit('teaspoon', session).get_shortname() == 'tsp'
  with pytest.raises(NoResultFound):
    get_unit('potato', session)

def test_get_metaconversions(session):
  create_all_units(session)
  create_all_conversions(session)
  # 4.5 Newtons at standard Earth gravity is about 459 grams
  conv = get_metaconversions(get_unit('N', session), 4.5, session)
  unit = list(conv.keys())[0]
  assert 'gram' == unit.name
  assert 459 == round(conv[unit])
  # on Mars, things are different
  conv = get_metaconversions(get_unit('g', session), 459, session, g=3.711)
  unit = get_unit('Newton', session)
  assert unit in conv.keys()
  assert 1.703 == round(conv[unit], 3)
  # a cc of water is a gram...
  conv = get_metaconversions(get_unit('L', session), 0.001, session)
  unit = list(conv.keys())[0]
  assert 'gram' == unit.name
  assert 1.0 == conv[unit]
  # but in olive oil...
  conv = get_metaconversions(get_unit('g', session), 55, session, density=0.916)
  unit = get_unit('liter', session)
  print(conv)
  assert unit in conv.keys()
  assert 0.05 == round(conv[unit], 2)
  #assert False




