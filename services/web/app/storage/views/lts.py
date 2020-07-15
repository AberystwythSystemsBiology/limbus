from ... import db
from ..models.lts import *
from ..models.shelf import FixedColdStorageShelf
from ...auth.views import UserView
from .shelf import BasicShelfView


def BasicLTSView(lts_id: int) -> dict:
    lts = (
        db.session.query(FixedColdStorage)
        .filter(FixedColdStorage.id == lts_id)
        .first_or_404()
    )

    return {
        "id": lts_id,
        "serial_number": lts.serial_number,
        "manufacturer": lts.manufacturer,
        "type": lts.type,
        "room_id": lts.room_id,
        "temperature": lts.temperature,
        "creation_date": lts.creation_date,
        "update_date": lts.update_date,
        "author_information": UserView(lts.author_id),
    }


def LTSView(lts_id: int) -> dict:
    data = BasicLTSView(lts_id)

    data["shelves"] = {
        x.id: BasicShelfView(x.id)
        for x in db.session.query(FixedColdStorageShelf)
        .filter(FixedColdStorageShelf.storage_id == lts_id)
        .all()
    }

    return data
