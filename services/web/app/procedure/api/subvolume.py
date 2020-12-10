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

from ...api import api, generic_new, generic_edit
from ...api.responses import *

from ...database import db
from flask import request, current_app, jsonify
from ...decorators import token_required

from marshmallow import ValidationError
from ...database import UserAccount, DiagnosticProcedureSubVolume

from ..views import (
    basic_diagnostic_procedure_subvolume_schema,
    new_diagnostic_procedure_subvolume_class
)


@api.route("/procedure/new/subvolume", methods=["POST"])
@token_required
def procedure_new_subvolume(tokenuser: UserAccount):
    return generic_new(
        db,
        DiagnosticProcedureSubVolume,
        new_diagnostic_procedure_subvolume_class,
        basic_diagnostic_procedure_subvolume_schema,
        request.json,
        tokenuser
        )