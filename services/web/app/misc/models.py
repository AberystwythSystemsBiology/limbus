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

from ..database import db, Base

from ..mixins import RefAuthorMixin


class Address(Base, RefAuthorMixin):
    street_address_one = db.Column(db.String(256), nullable=False)
    street_address_two = db.Column(db.String(256))
    city = db.Column(db.String(128), nullable=False)
    county = db.Column(db.String(128))
    post_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(2), nullable=False)


class SiteInformation(Base, RefAuthorMixin):
    miabis_id = db.Column(db.String(128))
    acronym = db.Column(db.String(64))
    name = db.Column(db.String(128))
    description = db.Column(db.String(128))
    url = db.Column(db.String(128))
    address_id = db.Column(db.Integer, db.ForeignKey("address.id"), nullable=False)
    address = db.relationship("Address", uselist=False)
