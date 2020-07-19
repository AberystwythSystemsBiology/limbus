from app import db

from ..auth.models import *

class Address(db.Model):
    __versioned__ = {}
    __tablename__ = "addresses"
    id = db.Column(db.Integer, primary_key=True)

    street_address_one = db.Column(db.String(256), nullable=False)
    street_address_two = db.Column(db.String(256))
    city = db.Column(db.String(128), nullable=False)
    county = db.Column(db.String(128))
    post_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(2), nullable=False)

    accounts = db.relationship("UserAccount")

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )


class SiteInformation(db.Model):
    __tablename__ = "sites"
    id = db.Column(db.Integer, primary_key=True)

    miabis_id = db.Column(db.String(128))
    acronym = db.Column(db.String(64))
    name = db.Column(db.String(128))

    description = db.Column(db.String(128))

    address_id = db.Column(db.Integer, db.ForeignKey("addresses.id"))

    url = db.Column(db.String(128))

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )
