from ... import db
from ..models.lts import *
from ...auth.views import UserView


def BasicLTSView(lts_id:int) -> dict:
    lts = db.session.query(FixedColdStorage).filter(FixedColdStorage.id == lts_id).first_or_404()

    return {
        "id": lts_id,
        "serial_number": lts.serial_number,
        "manufacturer": lts.manufacturer,
        "type": lts.type,
        "creation_date": lts.creation_date,
        "update_date": lts.update_date,
        "author_information": UserView(lts.author_id)
    }