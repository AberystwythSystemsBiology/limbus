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

from ..models import (
    DiagnosticProcedure,
)

from ...extensions import ma

from sqlalchemy_continuum import version_class, parent_class
import marshmallow_sqlalchemy as masql
from marshmallow import fields
from marshmallow_enum import EnumField

from ...auth.views import BasicUserAccountSchema


class NewDiagnosticProcedureSchema(masql.SQLAlchemySchema):
    class Meta:
        model = DiagnosticProcedure

    procedure = masql.auto_field()
    code = masql.auto_field()
    reference = masql.auto_field()
    sub_volume_id = masql.auto_field()


new_diagnostic_procedure_schema = NewDiagnosticProcedureSchema()

class BasicDiagnosticProcedureSchema(masql.SQLAlchemySchema):
    class Meta:
        model = DiagnosticProcedure

    id = masql.auto_field()
    procedure = masql.auto_field()
    code = masql.auto_field()
    reference = masql.auto_field()
    sub_volume_id = masql.auto_field()

basic_diagnostic_procedure_schema = BasicDiagnosticProcedureSchema()
basic_diagnostic_procedure__schema = BasicDiagnosticProcedureSchema(many=True)