FROM ubuntu:18.04

MAINTAINER "Keiron O'Shea <keo7@aber.ac.uk>"

RUN apt update
RUN apt install -y curl python3 python3-pip gv

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN curl -sL https://deb.nodesource.com/setup_10.x | bash - \
    && apt-get install -y nodejs

RUN npm install yarn -g

WORKDIR /limbus
ADD . /limbus

RUN pip3 install wheel && pip3 install -r requirements.txt