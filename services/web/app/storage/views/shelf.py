from ... import db

from ..models import *
from ...auth.views import UserView

def BasicShelfView(shelf_id: int) -> dict:
    shelf = db.session.query(FixedColdStorageShelf).filter(FixedColdStorageShelf.id == shelf_id).first_or_404()

    return {
        "id": shelf.id,
        "name": shelf.name,
        "creation_date": shelf.creation_date,
        "update_date": shelf.update_date,
        "author_information": UserView(shelf.author_id)
    }

def ShelfView(shelf_id: int) -> dict:

    data = BasicShelfView(shelf_id)

    return data