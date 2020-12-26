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
    DiagnosticProcedureVolume,
)

from ...extensions import ma

from sqlalchemy_continuum import version_class, parent_class
import marshmallow_sqlalchemy as masql
from marshmallow import fields
from marshmallow_enum import EnumField

from ...auth.views import BasicUserAccountSchema
from .tree import BasicDiagnosticProcedureSubVolumeSchema
from .pclass import BasicDiagnosticProcedureClassSchema


class NewDiagnosticProcedureVolumeSchema(masql.SQLAlchemySchema):
    class Meta:
        model = DiagnosticProcedureVolume

    id = masql.auto_field()
    name = masql.auto_field()
    code = masql.auto_field()
    class_id = masql.auto_field()


new_diagnostic_procedure_volume_class = NewDiagnosticProcedureVolumeSchema()


class DiagnosticProcedureVolumeSchema(masql.SQLAlchemySchema):
    class Meta:
        model = DiagnosticProcedureVolume

    id = masql.auto_field()
    name = masql.auto_field()
    code = masql.auto_field()

    subvolumes = ma.Nested(BasicDiagnosticProcedureSubVolumeSchema(many=True))
    creation_date = ma.Date()
    update_date = ma.Date()
    author = ma.Nested(BasicUserAccountSchema, many=False)

    pclass = ma.Nested(BasicDiagnosticProcedureClassSchema())

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("api.procedure_view_class", id="<id>", _external=True),
            "new_subvolume": ma.URLFor(
                "procedure.new_subvolume", id="<id>", _external=True
            ),
        }
    )


diagnostic_procedure_volume_schema = DiagnosticProcedureVolumeSchema()


class BasicDiagnosticProcedureVolumeSchema(masql.SQLAlchemySchema):
    class Meta:
        model = DiagnosticProcedureVolume

    id = masql.auto_field()
    name = masql.auto_field()
    code = masql.auto_field()


basic_diagnostic_procedure_volume_schema = BasicDiagnosticProcedureVolumeSchema()
basic_diagnostic_procedure_volumes_schema = BasicDiagnosticProcedureVolumeSchema(
    many=True
)
