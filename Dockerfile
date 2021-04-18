FROM python:3.9-alpine

RUN apk add shadow

RUN useradd -ms /bin/sh user

RUN mkdir /app

RUN chown user /app

COPY requirements.txt /app

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

ENTRYPOINT python main.py

