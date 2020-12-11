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
    DiagnosticProcedureSubVolume,
)

from ...extensions import ma

from sqlalchemy_continuum import version_class, parent_class
import marshmallow_sqlalchemy as masql
from marshmallow import fields
from marshmallow_enum import EnumField

from ...auth.views import BasicUserAccountSchema
from .volume import BasicDiagnosticProcedureVolumeSchema

class NewDiagnosticProcedureSubVolumeSchema(masql.SQLAlchemySchema):
    class Meta:
        model = DiagnosticProcedureSubVolume

    id = masql.auto_field()
    name = masql.auto_field()
    code = masql.auto_field()
    reference = masql.auto_field()
    volume_id = masql.auto_field()


new_diagnostic_procedure_subvolume_class = NewDiagnosticProcedureSubVolumeSchema()


class DiagnosticProcedureSubVolumeSchema(masql.SQLAlchemySchema):
    class Meta:
        model = DiagnosticProcedureSubVolume

    id = masql.auto_field()
    name = masql.auto_field()
    code = masql.auto_field()

    creation_date = ma.Date()
    update_date = ma.Date()
    author = ma.Nested(BasicUserAccountSchema, many=False)
    
    volume = ma.Nested(BasicDiagnosticProcedureVolumeSchema())

    _links = ma.Hyperlinks({
        "new_procedure": ma.URLFor("procedure.new_procedure", id="<id>", _external=True)
    })

diagnostic_procedure_subvolume_schema = DiagnosticProcedureSubVolumeSchema()
diagnostic_procedure_subvolumes_schema = DiagnosticProcedureSubVolumeSchema(many=True)

class BasicDiagnosticProcedureSubVolumeSchema(masql.SQLAlchemySchema):
    class Meta:
        model = DiagnosticProcedureSubVolume

    id = masql.auto_field()
    name = masql.auto_field()
    code = masql.auto_field()

basic_diagnostic_procedure_subvolume_schema = BasicDiagnosticProcedureSubVolumeSchema()
basic_diagnostic_procedure_subvolumes_schema = BasicDiagnosticProcedureSubVolumeSchema(many=True)