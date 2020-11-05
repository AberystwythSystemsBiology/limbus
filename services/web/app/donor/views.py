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

from .models import Donor
#from ..auth.views import UserView

from sqlalchemy_continuum import version_class, parent_class
from ..extensions import ma
import marshmallow_sqlalchemy as masql
from marshmallow import fields
from marshmallow_enum import EnumField

from ..auth.views import BasicUserAccountSchema
from .enums import BiologicalSexTypes, DonorStatusTypes, RaceTypes



class DonorSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Donor
    
    id = masql.auto_field()

    age = masql.auto_field()
    sex = EnumField(BiologicalSexTypes)
    status = EnumField(DonorStatusTypes)
    death_date = fields.Date()

    weight = fields.Float()
    height = fields.Float()

    race = EnumField(RaceTypes)

    author = ma.Nested(BasicUserAccountSchema)
    updater = ma.Nested(BasicUserAccountSchema)

    creation_date = fields.Date()
    update_date = fields.Date()


donor_schema = DonorSchema()
donors_schema = DonorSchema(many=True)


# def DonorIndexView():
#     donors = db.session.query(Donors).all()

#     data = {}

#     for donor in donors:
#         data[donor.id] = {
#             "age": donor.age,
#             "sex": donor.sex,
#             "status": donor.status,
#             "creation_date": donor.creation_date,
#             "user_information": UserView(donor.author_id),
#         }

#     return data


# def prepare_changeset(versions_list: list) -> dict:
#     data = {}

#     updater = None
#     for index, version in enumerate(versions_list[1:]):
#         changeset = {
#             prev: new for (prev, new) in version.changeset.items() if new != prev
#         }
#         if "updater_id" in changeset:
#             updater = UserView(changeset["updater_id"][1])
#         changeset["updater_id"] = updater
#         data[index] = changeset

#     return data


# def DonorView(donor_id):
#     donor = db.session.query(Donors).filter(Donors.id == donor_id).first_or_404()

#     data = {
#         "id": donor.id,
#         "age": donor.age,
#         "sex": donor.sex,
#         "status": donor.status,
#         "death_date": donor.death_date,
#         "race": donor.race,
#         "height": donor.height,
#         "weight": donor.weight,
#         "creation_date": donor.creation_date,
#         "update_date": donor.update_date,
#         "user_information": UserView(donor.author_id),
#         "versions": prepare_changeset(donor.versions),
#     }

#     return data
