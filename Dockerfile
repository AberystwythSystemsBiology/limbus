
FROM ubuntu:18.04

MAINTAINER "Keiron O'Shea <keo7@aber.ac.uk>"

RUN apt-get update && apt-get install \
  -y --no-install-recommends curl python3 python3-virtualenv

RUN curl -sL https://deb.nodesource.com/setup_6.x | bash - \
    && apt-get install -y nodejs npm

RUN python3 -m virtualenv --python=/usr/bin/python3 $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN npm install yarn -g

WORKDIR /limbus

CMD sh -c "pip install -r requirements.txt && yarn install"