from app import db


class Address(db.Model):
    __tablename__ = "addresses"
    id = db.Column(db.Integer, primary_key=True)

    street_address_one = db.Column(db.String(256))
    street_address_two = db.Column(db.String(256))
    city = db.Column(db.String(128))
    county = db.Column(db.String(128))
    post_code = db.Column(db.String(20))
    country = db.Column(db.String(2), nullable=False)

    creation_date = db.Column(db.DateTime,
                              server_default=db.func.now(),
                              nullable=False)
    update_date = db.Column(db.DateTime,
                            server_default=db.func.now(),
                            server_onupdate=db.func.now(),
                            nullable=False)

class BiobankInformation(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    miabis_id = db.Column(db.String(128))
    acronym = db.Column(db.String(64))
    name = db.Column(db.String(128))

    description = db.Column(db.String(128))

    url = db.Column(db.String(128))
