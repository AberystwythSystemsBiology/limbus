from app import db

class Biobank(db.Model):
    __tablename__ = "biobanks"

    # Textual string of letters starting with the country code
    # (according to standard ISO1366 alpha2) followed by the underscore
    #  “_” and post-fixed by a biobank ID or name specified by its
    # juristic person (nationally specific)

    id = db.Column(db.String(20), primary_key=True)

    acronym = db.Column(db.String(10))

    name = db.Column(db.String(128), required=True)
    url = db.Column(db.String(256), required=True)

    # juristic_person = db.Column(db.String(256))

    country = db.Column(db.String(2), required=True)

    description = db.Column(db.String(256), required=True)

class JuristicPerson(db.Model):
    __table__ = "juristicpersons"

    id = db.Column(db.Integer, primary_key=True)
    