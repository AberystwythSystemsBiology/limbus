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

from sqlalchemy.ext.declarative import declared_attr
from .database import db


class RefAuthorMixin(object):
    @declared_attr
    def author_id(cls):
        return db.Column(db.Integer, db.ForeignKey("useraccount.id"))

    @declared_attr
    def author(cls):
        return db.relationship(
            "UserAccount", primaryjoin="UserAccount.id==%s.author_id" % cls.__name__
        )


class RefEditorMixin(object):
    @declared_attr
    def editor_id(cls):
        return db.Column(db.Integer, db.ForeignKey("useraccount.id"))

    @declared_attr
    def editor(cls):
        return db.relationship(
            "UserAccount", primaryjoin="UserAccount.id==%s.editor_id" % cls.__name__
        )
