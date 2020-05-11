#! /usr/bin/env sh

#echo "Running inside /app/prestart.sh, you could add migrations to this file, e.g.:"

#echo "
#! /usr/bin/env bash

# Let the DB start
#sleep 10;
# Run migrations
#alembic upgrade head
#"

# fork a bash to wait for MySQL and run migrations
command="/app/wait-for-it.sh -h ${MYSQL_HOST} -p ${MYSQL_PORT:-3306} -t 1800 -- alembic upgrade head"
#echo $command
bash -c "${command}"
