FROM ubuntu:18.04

MAINTAINER "Keiron O'Shea <keo7@aber.ac.uk>"

RUN apt-get update && apt-get install \
  -y curl python3 python3-venv

RUN curl -sL https://deb.nodesource.com/setup_6.x | bash - \
    && apt-get install -y nodejs npm

RUN npm install yarn -g

WORKDIR /limbus