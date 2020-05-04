FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7

RUN apk update && apk add g++ make python3-dev mariadb-dev libxml2-dev libxslt-dev

RUN pip3 install --upgrade pip
COPY requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt

COPY ./app /app

# use parent's default CMD