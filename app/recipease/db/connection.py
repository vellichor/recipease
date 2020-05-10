from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

def get_engine(db, host=os.environ.get('MYSQL_HOST'),
                user=os.environ.get('MYSQL_USER'),
                password=os.environ.get('MYSQL_PASSWORD'),
                port=os.environ.get('MYSQL_PORT', '3306')):
  url="mysql://{}:{}@{}:{}/{}".format(user, password, host, port, db)
  return create_engine(url, pool_recycle=3600)


engine = get_engine(db="recipease")
Session = sessionmaker(bind=engine)

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
