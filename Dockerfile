FROM ubuntu:18.04

MAINTAINER "Keiron O'Shea <keo7@aber.ac.uk>"

RUN apt-get update && apt-get install \
  -y --no-install-recommends curl python3 python3-virtualenv

RUN curl -sL https://deb.nodesource.com/setup_6.x | bash - \
    && apt-get install -y nodejs npm

RUN npm install yarn -g

ENV VIRTUAL_ENV="/opt/venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ENV FLASK_CONFIG="dev"
ENV FLASK_APP="/limbus/limbus/app"
ENV LANG="C.UTF-8"
ENV LC_ALL="C.UTF-8"

WORKDIR /limbus

CMD sh -c "python3 -m virtualenv $VIRTUAL_ENV && pip install -r requirements.txt && yarn install"
