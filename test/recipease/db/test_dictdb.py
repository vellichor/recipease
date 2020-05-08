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
  # make another one. it should not create an id, but should give
  # the same actual object from the session.
  unit_dict['class'] = Unit
  unit_2 = get_or_save_simple_dict(unit_dict, empty_db_session)
  assert unit_1.id == unit_2.id
  assert unit_1 is unit_2 # same actual object!
  # now, save one with the same uniques and modified secondary attributes!!
  unit_dict['plural_name'] = 'cupopodae'
  unit_3 = get_or_save_simple_dict(unit_dict, empty_db_session)
  assert unit_3.plural_name == 'cupopodae'
  assert unit_1.plural_name == 'cupopodae'

def test_save_list(empty_db_session):
  # make an image list that does NOT already contain its images
  image_set = get_or_save_simple_dict({
    'class': ImageSet
    }, empty_db_session)
  # make the images explicitly
  images = [
    {
      'class': Image,
      'url': 'https://scontent-lax3-1.xx.fbcdn.net/v/t1.0-9/s960x960/95424293_10216038224616437_8689915701164507136_o.jpg?_nc_cat=108&_nc_sid=1480c5&_nc_ohc=D_A9wGqJn-4AX-VaMUB&_nc_ht=scontent-lax3-1.xx&_nc_tp=7&oh=e9bf59f0f3ac3af606126cf9f1cf7ace&oe=5EDC6DC3'
    },
    {
      'class': Image,
      'url': 'https://scontent-lax3-1.xx.fbcdn.net/v/t1.0-9/95822761_10216038229336555_5558257331126403072_n.jpg?_nc_cat=110&_nc_sid=1480c5&_nc_ohc=JJldsV31vdwAX-d9zod&_nc_ht=scontent-lax3-1.xx&oh=85ae57098d90a5b8070227ff3e809c79&oe=5ED967F8'
    }
  ]
  save_list(images, empty_db_session, image_set_id=image_set.id)
  # save_list doesn't return anything, so instead make sure we can get objects back from the db
  results = empty_db_session.query(Image).filter(Image.image_set_id==image_set.id).all()
  print(results)
  assert len(results) == 2
  assert any(map(lambda x: x.url == images[0]['url'], results))
  assert any(map(lambda x: x.url == images[1]['url'], results))

def test_save_dict(empty_db_session):
  # conversions have nested dictionaries
  conv_dict = {
    'class': Conversion,
    'num_unit_id': {
      'class': Unit,
      'name': 'cup',
      'shortname': 'c'
    },
    'num_qty': 2,
    'denom_unit_id': {
      'class': Unit,
      'name': 'pint',
      'shortname': 'pt'
    },
    'denom_qty': 1
  }
  conv = save_dict(conv_dict, empty_db_session)
  # the saved dictionary should now contain a numeric index
  assert type(conv_dict['num_unit_id']) == int
  # if we retrieve that it should be the right thing
  results = empty_db_session.query(Unit).filter(Unit.id == conv_dict['num_unit_id']).all()
  assert len(results) == 1
  assert results[0].name == 'cup'



