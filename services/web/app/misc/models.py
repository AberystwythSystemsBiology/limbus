from app import db, Base
from ..base import  RefAuthorMixin

class Address(Base):

    street_address_one = db.Column(db.String(256), nullable=False)
    street_address_two = db.Column(db.String(256))
    city = db.Column(db.String(128), nullable=False)
    county = db.Column(db.String(128))
    post_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(2), nullable=False)



class SiteInformation(Base):

    miabis_id = db.Column(db.String(128))
    acronym = db.Column(db.String(64))
    name = db.Column(db.String(128))

    description = db.Column(db.String(128))

    url = db.Column(db.String(128))

    #Add 