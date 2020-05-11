from .. import db
from .models import Donors
from ..auth.views import UserView

def DonorIndexView():
    donors = db.session.query(Donors).all()

    data = {}

    for donor in donors:
        data[donor.id] = {
            "age": donor.age,
            "sex": donor.sex,
            "status": donor.status,
            "creation_date": donor.creation_date,
            "user_information": UserView(donor.author_id)
        }

    return data

def DonorView(donor_id):
    donor = db.session.query(Donors).filter(Donors.id == donor_id).first_or_404()

    data = {
        "id": donor.id,
        "age": donor.age,
        "sex": donor.sex,
        "status": donor.status,
        "death_date": donor.death_date,
        "race": donor.race,
        "height": donor.height,
        "weight": donor.weight,
        "creation_date": donor.creation_date,
        "update_date": donor.update_date,
        "user_information": UserView(donor.author_id)
    }

    return data

    