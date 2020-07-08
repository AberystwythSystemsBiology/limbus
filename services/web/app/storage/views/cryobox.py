from ... import db
from ..models import CryovialBox
from ...auth.views import UserView


def CryoboxIndexView() -> dict:
    boxes = db.session.query(CryovialBox).all()

    data = {}

    for b in boxes:
        d = BasicCryoboxView(b.id)
        del d["id"]
        data[b.id] = d

    return data


def BasicCryoboxView(cryo_id: int) -> dict:
    box = db.session.query(CryovialBox).filter(CryovialBox.id == cryo_id).first_or_404()

    return {
        "id": cryo_id,
        "serial": box.serial,
        "num_rows": box.num_rows,
        "num_cols": box.num_cols,
        "author_information": UserView(box.author_id),
    }
