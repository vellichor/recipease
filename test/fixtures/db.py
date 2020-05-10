import test_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils.functions import database_exists, create_database, \
                                        drop_database

import recipease.db.connection as conn
from recipease.db.models import Base

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