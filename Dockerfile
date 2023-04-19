FROM python:3.9-alpine

RUN apk update
RUN pip install --no-cache-dir --upgrade pip

WORKDIR /usr/src/app