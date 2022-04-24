FROM ubuntu:20.04

LABEL authors="Keiron O'Shea <keo7@aber.ac.uk>, Chuan Lu <cul@aber.ac.uk>"

ARG DEBIAN_FRONTEND=noninteractive

ENV TZ=Europe/London
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y curl 

RUN curl -sL https://deb.nodesource.com/setup_14.x | bash - \
    && apt-get install -y nodejs

RUN apt-get -y install python3 python3-pip python3-wheel python3-setuptools \ 
    gv libffi-dev libcairo2-dev libpango1.0-dev libgirepository1.0-dev



RUN npm install yarn -g

WORKDIR /limbus
ADD . /limbus

RUN pip3 install -r requirements.txt