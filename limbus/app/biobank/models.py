from app import db

class Biobank(db.Model):
    __tablename__ = "biobank"

    id = db.Column(db.Integer(), primary_key=True)

    acronym = db.Column(db.String)

    url = db.Column(db.String)

    #juristic_person_id = 0

    #country_code = 0

    #description = 0


class BiobankSampleCollection(db.Model):
    pass

class SampleCollection(db.Model):
    pass

class BiobankAttributeLists(db.Model):
    pass

class BiobankAttributeListMaster(db.Model):
    pass

class Sample(db.Model):
    pass