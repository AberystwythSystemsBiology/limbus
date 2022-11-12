# Copyright (C) 2019  Keiron O'Shea <keo7@aber.ac.uk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os

SUPPORTED_LANGUAGES = {"en": "English", "cy": "Cymraeg"}
BABEL_DEFAULT_LOCALE = "en"

DEBUG = os.environ["DEBUG"]

MAIL_SERVER = os.environ["MAIL_SERVER"]
MAIL_USERNAME = os.environ["MAIL_USERNAME"]
MAIL_PASSWORD = os.environ["MAIL_PASSWORD"]
MAIL_SENDER = os.environ["MAIL_USERNAME"]

MAIL_PORT = 587
MAIL_USE_TLS = 1

if "MAIL_PORT" in os.environ:
    MAIL_PORT = os.environ["MAIL_PORT"]

if "MAIL_USE_TLS" in os.environ:
    MAIL_USE_TLS = os.environ["MAIL_USE_TLS"]

if "MAIL_USE_SSL" in os.environ:
    MAIL_USE_SSL = os.environ["MAIL_USE_SSL"]
    MAIL_USE_TLS = 0

if "SQLALCHEMY_ECHO" in os.environ:
    SQLALCHEMY_ECHO = os.environ["SQLALCHEMY_ECHO"]

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False

SQLALCHEMY_DATABASE_URI = (
    "postgresql+psycopg2://{user}:{passwd}@{dbhost}:5432/{db}".format(
        user=os.environ["POSTGRES_USER"],
        passwd=os.environ["POSTGRES_PASSWORD"],
        db=os.environ["POSTGRES_DB"],
        dbhost=os.environ["POSTGRES_HOST"],
    )
)

SECRET_KEY = os.environ["SECRET_KEY"]
WTF_CSRF_SECRET_KEY = os.environ["WTF_CSRF_SECRET_KEY"]
DOCUMENT_DIRECTORY = os.environ["DOCUMENT_DIRECTORY"]
TMP_DIRECTORY = os.environ["TMP_DIRECTORY"]
