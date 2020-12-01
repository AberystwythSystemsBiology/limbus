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

from sqlalchemy.ext.declarative import as_declarative, declared_attr
from .database import db
import datetime


@as_declarative()
class BaseModel(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @declared_attr
    def __mapper_args__(cls):
        return {"eager_defaults": True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    created_on = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    is_locked = db.Column(db.Boolean, default=False)

    updated_on = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

    def update(self, values):
        for attr, values in values.items():
            setattr(self, attr, values)

        self.updated_on = db.func.now()
