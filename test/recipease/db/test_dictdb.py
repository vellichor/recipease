import test_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils.functions import database_exists, create_database, drop_database

import recipease.db.connection as conn

from recipease.db.models import *
from recipease.db.dictdb import *


import pytest

@pytest.fixture
def empty_db_session():
  # we are gonna create a connection to local but we're going to do it on a random database.
  db_name = 'potatopants' # TODO: random string
  engine = conn.get_engine(db_name)
  try:
    if not database_exists(engine.url):
      create_database(engine.url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # do the test work in this session's scope
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
  finally:
      # drop our temporary database
    if database_exists(engine.url):
      drop_database(engine.url)

def test_class_to_foreign_key():
  assert 'unit_id' == class_to_foreign_key(Unit)

def test_get_or_save_simple_dict(empty_db_session):
  unit_dict = {'class': Unit,
                'name': 'cup',
                'shortname': 'c'}
  unit_1 = get_or_save_simple_dict(unit_dict, empty_db_session)
  # check the unit id, there should be one
  unit_id = unit_1.id
  print(unit_1)
  print(unit_id)
  # make another one. it should not create an id, but should give the same one.
  unit_dict['class'] = Unit
  unit_2 = get_or_save_simple_dict(unit_dict, empty_db_session)
  print(unit_2)
  print(unit_2.id)
  assert unit_1.id == unit_2.id





