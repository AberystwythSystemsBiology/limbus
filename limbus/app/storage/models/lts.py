from app import db
from ..enums import FixedColdStorageTemps, FixedColdStorageType


class FixedColdStorage(db.Model):
    __tablename__ = "fixed_cold_storage"

    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.String)
    manufacturer = db.Column(db.String)

    temperature = db.Column(db.Enum(FixedColdStorageTemps))

    type = db.Column(db.Enum(FixedColdStorageType))

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"))

    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))


class DeviceManualToFixedColdStorage(db.Model):
    __tablename__ = "device_manual_to_fixed_cold_storage"
    id = db.Column(db.Integer, primary_key=True)

    storage_id = db.Column(db.Integer, db.ForeignKey("fixed_cold_storage.id"))
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id"))

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
