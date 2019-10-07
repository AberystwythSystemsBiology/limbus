from app import db
from enum import Enum

class TitleType(Enum):
    MR = "Mr."
    MRS = "Mrs."
    MS = "Ms."
    MISS = "Miss."
    M = "M."
    MX = "Mx."
    MASTER = "Master."
    DR = "Dr."
    PROF = "Prof."

class ContactInformation(db.Model):
    __tablename__ = "contact_information"

    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(60), unique=True)
    title = db.Column(db.Enum(TitleType))
    first_name = db.Column(db.String(60))
    last_name = db.Column(db.String(60))
    phone_number = db.Column(db.String(12))
    street_address_one = db.Column(db.String(256))
    street_address_two = db.Column(db.String(256))
    city = db.Column(db.String(128))
    county = db.Column(db.String(128))
    country = db.Column(db.String(2), nullable=False)

class JuristicPersonType(Enum):
    UNIVERSITY = "University"
    INDIVIDUAL = "Individual"
    ORGANISATION = "Organisation"
    RESEARCHER = "Researcher"

class JuristicPerson(db.Model):
    __tablename__ = "juristic_person"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(128))
    type = db.Column(db.Enum(TitleType))


class ResearcherInformation(db.Model):
    __tablename__ = "researcher_information"

    id = db.Column(db.Integer(), primary_key=True)
    orcid = db.Column(db.String(30), unique=True)
