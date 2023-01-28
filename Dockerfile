FROM python:3.9-slim-buster

ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN apt-get update && apt-get install -y libpq-dev
RUN apt-get update && apt-get install -y python3-psycopg2
RUN pip3 install Psycopg2-binary
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . /code/