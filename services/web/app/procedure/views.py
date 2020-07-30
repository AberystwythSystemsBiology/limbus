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
from .models import (
    DiagnosticProcedureClass,
    DiagnosticProcedureVolume,
    DiagnosticProcedureSubheading,
    DiagnosticProcedure,
)
from ..auth.views import UserView


def DiagnosticProceduresIndexView() -> dict:
    data = {}

    for procedure in db.session.query(DiagnosticProcedureClass).all():
        data[procedure.id] = {
            "name": procedure.name,
            "version": procedure.version,
            "upload_date": procedure.creation_date,
            "update_date": procedure.update_date,
            "user_information": UserView(procedure.author_id),
        }

    return data


def DiagnosticProcedureView(proc_id) -> dict:
    proc = (
        db.session.query(DiagnosticProcedureClass)
        .filter(DiagnosticProcedureClass.id == proc_id)
        .first_or_404()
    )

    volumes = (
        db.session.query(DiagnosticProcedureVolume)
        .filter(DiagnosticProcedureVolume.class_id == proc_id)
        .all()
    )

    data = {
        "id": proc.id,
        "name": proc.name,
        "version": proc.version,
        "upload_date": proc.creation_date,
        "update_date": proc.update_date,
        "user_information": UserView(proc.author_id),
        "volumes": {},
    }

    for volume in volumes:
        data["volumes"][volume.id] = {
            "code": volume.code,
            "name": volume.name,
            "subheadings": {},
        }

        subheadings = (
            db.session.query(DiagnosticProcedureSubheading)
            .filter(DiagnosticProcedureSubheading.volume_id == volume.id)
            .all()
        )

        for sh in subheadings:

            diagnostic_procs = (
                db.session.query(DiagnosticProcedure)
                .filter(DiagnosticProcedure.subheading_id == sh.id)
                .all()
            )

            codes = {}

            for proc in diagnostic_procs:
                codes[proc.id] = {"code": proc.code, "procedure": proc.procedure}

            data["volumes"][volume.id]["subheadings"][sh.id] = {
                "code": sh.code,
                "subheading": sh.subheading,
                "codes": codes,
            }

    return data
