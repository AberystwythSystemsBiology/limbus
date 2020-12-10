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


from ..database import db, Base
from ..mixins import RefAuthorMixin, RefEditorMixin


class DiagnosticProcedureClass(Base, RefAuthorMixin, RefEditorMixin):
    name = db.Column(db.String)
    version = db.Column(db.String)
    description = db.Column(db.String)

    volumes = db.relationship("DiagnosticProcedureVolume", uselist=True)


class DiagnosticProcedureVolume(Base, RefAuthorMixin, RefEditorMixin):
    code = db.Column(db.String(5))
    name = db.Column(db.String)
    class_id = db.Column(db.Integer, db.ForeignKey("diagnosticprocedureclass.id"))

    subvolumes = db.relationship("DiagnosticProcedureSubVolume", uselist=True)

class DiagnosticProcedureSubVolume(Base, RefAuthorMixin, RefEditorMixin):
    code = db.Column(db.String(5))
    name = db.Column(db.String())
    reference = db.Column(db.String(256))
    volume_id = db.Column(db.Integer, db.ForeignKey("diagnosticprocedurevolume.id"))

    procedures = db.relationship("DiagnosticProcedure", uselist=True)

class DiagnosticProcedure(Base, RefAuthorMixin, RefEditorMixin):
    code = db.Column(db.String(5))
    procedure = db.Column(db.String())
    reference = db.Column(db.String(256))

    sub_volume_id = db.Column(
        db.Integer, db.ForeignKey("diagnosticproceduresubvolume.id")
    )

