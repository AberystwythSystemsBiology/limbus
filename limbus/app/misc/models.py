from app import db

class AddressInformation(db.Model):
    __tablename__ = "address_information"

    id = db.Column(db.Integer, primary_key=True)

    street_address_one = db.Column(db.String(256))
    street_address_two = db.Column(db.String(256))
    city = db.Column(db.String(128))
    county = db.Column(db.String(128))
    country = db.Column(db.String(2), nullable=False)

class BiobankInformation(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    miabis_id = db.Column(db.String(128))
    acronym = db.Column(db.String(64))
    name = db.Column(db.String(128))

    description = db.Column(db.String(128))

    url = db.Column(db.String(128))