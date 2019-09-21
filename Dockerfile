
FROM ubuntu:18.04

MAINTAINER Keiron O'Shea <keo7@aber.ac.uk>
RUN apt-get update && apt-get install \
  -y --no-install-recommends python3 python3-virtualenv git
ADD ./ /limbus
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m virtualenv --python=/usr/bin/python3 $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
