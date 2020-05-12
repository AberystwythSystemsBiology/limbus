from app import db
from .enums import *

class Donors(db.Model):
    __versioned__ = {}
    __tablename__ = "donors"

    id = db.Column(db.Integer, primary_key=True)

    uuid = db.Column(db.String(36))

    age = db.Column(db.Integer)
    sex = db.Column(db.Enum(BiologicalSexTypes))
    status = db.Column(db.Enum(DonorStatusTypes))
    death_date = db.Column(db.DateTime)
    
    weight = db.Column(db.Float)
    height = db.Column(db.Float)

    race = db.Column(db.Enum(RaceTypes))

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    updater_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )