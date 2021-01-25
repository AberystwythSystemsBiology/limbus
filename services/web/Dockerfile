FROM ubuntu:18.04

MAINTAINER "Keiron O'Shea <keo7@aber.ac.uk>"

RUN apt update
RUN apt upgrade -y
RUN apt install -y curl python3 python3-pip python3-wheel python3-setuptools gv libffi-dev libcairo2-dev libpango1.0-dev

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV LANG=C.UTF-8

RUN curl -sL https://deb.nodesource.com/setup_10.x | bash - \
    && apt-get install -y nodejs

RUN npm install yarn -g

WORKDIR /limbus
ADD . /limbus