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
