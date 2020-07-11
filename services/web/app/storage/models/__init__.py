from app import db

from .site import *
from .room import *
from .lts import *
from .shelf import *
from .cryobox import *
from ..enums import EntityToStorageTpye

class EntityToStorage(db.Model):
    __versioned__ = {}
    __tablename__ = "entities_to_storage"

    id = db.Column(db.Integer, primary_key=True)

    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"))
    box_id = db.Column(db.Integer, db.ForeignKey("cryovial_boxes.id"))
    shelf_id = db.Column(db.Integer, db.ForeignKey("fixed_cold_storage_shelves.id"))
    storage_type = db.Column(db.Enum(EntityToStorageTpye))

    row = db.Column(db.Integer)
    col = db.Column(db.Integer)

    entered = db.Column(db.DateTime)
    entered_by = db.Column(db.String(5))

    removed = db.Column(db.Boolean)
    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))