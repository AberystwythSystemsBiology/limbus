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
    DiagnosticProcedureClass,
)

from ...extensions import ma

from sqlalchemy_continuum import version_class, parent_class
import marshmallow_sqlalchemy as masql
from marshmallow import fields
from marshmallow_enum import EnumField

from ...auth.views import BasicUserAccountSchema


class NewDiagnosticProcedureClass(masql.SQLAlchemySchema):
    class Meta:
        model = DiagnosticProcedureClass

    name = masql.auto_field()
    description = masql.auto_field()
    version = masql.auto_field()


new_diagnostic_procedure_class = NewDiagnosticProcedureClass()


class BasicDiagnosticProcedureClassSchema(masql.SQLAlchemySchema):
    class Meta:
        model = DiagnosticProcedureClass

    id = masql.auto_field()
    name = masql.auto_field()
    description = masql.auto_field()
    version = masql.auto_field()
    author = ma.Nested(BasicUserAccountSchema, many=False)
    creation_date = ma.Date()

    _links = ma.Hyperlinks({
        "self": ma.URLFor("api.procedure_view_class", id="<id>", _external=True)
    })

basic_diagnostic_procedure_class_schema = BasicDiagnosticProcedureClassSchema()
basic_diagnostic_procedure_classes_schema = BasicDiagnosticProcedureClassSchema(many=True)

class DiagnosticProcedureClassSchema(masql.SQLAlchemySchema):
    class Meta:
        model = DiagnosticProcedureClass

    id = masql.auto_field()
    name = masql.auto_field()
    description = masql.auto_field()
    version = masql.auto_field()
    creation_date = ma.Date()
    update_date = ma.Date()
    author = ma.Nested(BasicUserAccountSchema, many=False)

    _links = ma.Hyperlinks({
        "self": ma.URLFor("api.procedure_view_class", id="<id>", _external=True),
        "new_volume": ma.URLFor("procedure.new_volume", id="<id>", _external=True)
    })


diagnostic_procedure_class_schema = DiagnosticProcedureClassSchema()