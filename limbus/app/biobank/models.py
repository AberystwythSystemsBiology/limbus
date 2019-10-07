from app import db

class Biobank(db.Model):
    __tablename__ = "biobank"

    id = db.Column(db.Integer(), primary_key=True)

    acronym = db.Column(db.String)

    url = db.Column(db.String)