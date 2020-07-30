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

from app import db
from ..enums import *


class SamplePatientConsentFormTemplateAssociation(db.Model):
    __tablename__ = "sample_pcf_associations"

    id = db.Column(db.Integer, primary_key=True)

    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"))
    template_id = db.Column(db.Integer, db.ForeignKey("consent_form_templates.id"))

    consent_id = db.Column(db.String)

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)


class SamplePatientConsentFormAnswersAssociation(db.Model):
    __tablename__ = "pcf_answers"

    id = db.Column(db.Integer, primary_key=True)

    sample_pcf_association_id = db.Column(
        db.Integer, db.ForeignKey("sample_pcf_associations.id")
    )

    checked = db.Column(db.Integer, db.ForeignKey("consent_form_template_questions.id"))

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
