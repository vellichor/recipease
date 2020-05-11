from logging.config import fileConfig
import os

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy_utils.functions import database_exists, create_database

from alembic import context

from recipease.db.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# We're actually going to set up the DB details from the system env.
host = os.environ.get('MYSQL_HOST', 'mysql')
user = os.environ.get('MYSQL_USER', 'mysql')
password = os.environ.get('MYSQL_PASSWORD', 'pass123')
port = os.environ.get('MYSQL_PORT', '3306')
db = os.environ.get('MYSQL_DB', 'recipease')
url = "mysql://{}:{}@{}:{}/{}".format(user, password, host, port, db)

# this will overwrite the ini-file sqlalchemy.url path
# with the path given in the config of the main code
config.set_main_option("sqlalchemy.url", url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.



def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # do the right thing even if no database existed yet!
    if not database_exists(connectable.url):
      create_database(connectable.url)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
