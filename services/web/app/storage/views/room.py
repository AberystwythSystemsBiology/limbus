from ... import db
from ..models.room import Room
from ..models.lts import FixedColdStorage
from ...auth.views import UserView
from .lts import BasicLTSView


def BasicRoomView(room_id: int) -> dict:
    r = db.session.query(Room).filter(Room.id == room_id).first_or_404()
    return {
        "id": r.id,
        "room_number": r.room_number,
        "building": r.building,
        "creation_date": r.creation_date,
        "site_id": r.site_id,
        "author_information": UserView(r.author_id),
    }


def RoomView(room_id: int) -> dict:
    data = BasicRoomView(room_id)

    data["storage"] = [
        BasicLTSView(x.id)
        for x in db.session.query(FixedColdStorage)
        .filter(FixedColdStorage.room_id == room_id)
        .all()
    ]

    return data
