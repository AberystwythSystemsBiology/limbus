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

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy_continuum import make_versioned
from sqlalchemy_continuum.plugins import PropertyModTrackerPlugin, FlaskPlugin
from sqlalchemy.orm import configure_mappers

db = SQLAlchemy()

from .base import BaseModel as BM

Base = declarative_base(cls=BM)
Base.query = db.session.query_property()

from .auth.models import *
from .misc.models import *
from .attribute.models import *
from .consent.models import *
from .document.models import *
from .protocol.models import *
from .sample.models import *

configure_mappers()