FROM python:3.9-alpine

RUN apk add shadow

RUN useradd -ms /bin/sh user

RUN mkdir /app

RUN chown user /app

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT python main.py

