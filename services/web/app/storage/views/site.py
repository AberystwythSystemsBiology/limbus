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

from ... import db

from ...misc.models import Address
from ..models import *
from ...auth.views import UserView
from .room import BasicRoomView


def BasicSiteView(site_id: int) -> dict:
    s = db.session.query(Site).filter(Site.id == site_id).first_or_404()
    return {
        "id": s.id,
        "name": s.name,
        "creation_date": s.creation_date,
        "address_id": s.address_id,
        "author_information": UserView(s.author_id),
    }


def SiteView(site_id: int) -> dict:
    data = BasicSiteView(site_id)

    address = (
        db.session.query(Address)
        .filter(Address.id == data["address_id"])
        .first_or_404()
    )

    data["address"] = {
        "street_address_one": address.street_address_one,
        "street_address_two": address.street_address_two,
        "city": address.city,
        "county": address.county,
        "post_code": address.post_code,
    }

    data["rooms"] = [
        BasicRoomView(x.id)
        for x in db.session.query(Room).filter(Room.site_id == site_id).all()
    ]

    return data
