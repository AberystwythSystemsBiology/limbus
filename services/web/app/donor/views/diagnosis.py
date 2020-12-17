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

from ...extensions import ma
from ...database import DonorDiagnosisEvent
from ...extensions import ma
import marshmallow_sqlalchemy as masql
from marshmallow_enum import EnumField

from ...auth.views import BasicUserAccountSchema
from ..enums import CancerStage

class NewDonorDiagnosisEventSchema(masql.SQLAlchemySchema):
    class Meta:
        model = DonorDiagnosisEvent

    donor_id = masql.auto_field()
    doid_ref = masql.auto_field()
    stage = EnumField(CancerStage)
    diagnosis_date = ma.Date()
    comments = masql.auto_field()
    

new_donor_diagnosis_event_schema = NewDonorDiagnosisEventSchema()


class DonorDiagnosisEventSchema(masql.SQLAlchemySchema):
    class Meta:
        model = DonorDiagnosisEvent

    id = masql.auto_field()
    donor_id = masql.auto_field()
    doid_ref = masql.auto_field()
    stage = EnumField(CancerStage)
    diagnosis_date = ma.Date()
    comments = masql.auto_field()

donor_diagnosis_event_schema = DonorDiagnosisEventSchema()
