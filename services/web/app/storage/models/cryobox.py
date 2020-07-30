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

from app import db


class CryovialBox(db.Model):
    __tablename__ = "cryovial_boxes"
    id = db.Column(db.Integer, primary_key=True)

    serial = db.Column(db.String)

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    removed = db.Column(db.Boolean)

    num_rows = db.Column(db.Integer)
    num_cols = db.Column(db.Integer)

    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
