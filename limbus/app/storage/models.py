from app import db
from .enums import *


class Site(db.Model):
    __tablename__ = "sites"
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(128))
    address_id = db.Column(db.Integer, db.ForeignKey("addresses.id"))

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))


class Room(db.Model):
    __tablename__ = "rooms"
    id = db.Column(db.Integer, primary_key=True)

    room_number = db.Column(db.String(256), nullable=False)
    building = db.Column(db.String(128))

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    site_id = db.Column(db.Integer, db.ForeignKey("sites.id"))

    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))


class FixedColdStorage(db.Model):
    __tablename__ = "fixed_cold_storage"

    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.String)
    manufacturer = db.Column(db.String)

    temperature = db.Column(db.Enum(FixedColdStorageTemps))
    num_shelves = db.Column(db.Integer, nullable=False)

    type = db.Column(db.Enum(FixedColdStorageType))

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    site_id = db.Column(db.Integer, db.ForeignKey("sites.id"))

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


class SampleToFixedColdStorage:
    __tablename__ = "sample_to_fixed_cold_storage"
    id = db.Column(db.Integer, primary_key=True)

    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"))
    storage_id = db.Column(db.Integer, db.ForeignKey("fixed_cold_storage.id"))

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))


class CryovialBox(db.Model):
    __tablename__ = "cryovial_boxes"
    id = db.Column(db.Integer, primary_key=True)

    serial = db.Column(db.String)

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    num_rows = db.Column(db.Integer)
    num_cols = db.Column(db.Integer)

    data = db.Column(db.JSON)

    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
