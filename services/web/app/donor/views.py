# Copyright (C) 2019  Keiron O'Shea <keo7@aber.ac.uk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from .. import db
from .models import Donors
from ..auth.views import UserView

from sqlalchemy_continuum import version_class, parent_class


def DonorIndexView():
    donors = db.session.query(Donors).all()

    data = {}

    for donor in donors:
        data[donor.id] = {
            "age": donor.age,
            "sex": donor.sex,
            "status": donor.status,
            "creation_date": donor.creation_date,
            "user_information": UserView(donor.author_id),
        }

    return data


def prepare_changeset(versions_list: list) -> dict:
    data = {}

    updater = None
    for index, version in enumerate(versions_list[1:]):
        changeset = {
            prev: new for (prev, new) in version.changeset.items() if new != prev
        }
        if "updater_id" in changeset:
            updater = UserView(changeset["updater_id"][1])
        changeset["updater_id"] = updater
        data[index] = changeset

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
        "user_information": UserView(donor.author_id),
        "versions": prepare_changeset(donor.versions),
    }

    return data
