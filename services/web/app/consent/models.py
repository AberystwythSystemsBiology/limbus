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

from app import db, Base
from ..mixins import RefAuthorMixin, RefEditorMixin
from .enums import ConsentType

class ConsentFormTemplate(Base, RefAuthorMixin, RefEditorMixin):
    __tablename__ = "consentformtemplate"
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(2048))
    version = db.Column(db.String(64))
    questions = db.relationship("ConsentFormTemplateQuestion", backref="consentformtemplate")

class ConsentFormTemplateQuestion(Base, RefAuthorMixin, RefEditorMixin):
    __tablename__ = "consentformtemplatequestion"
    question = db.Column(db.String(2048), nullable=False)
    type = db.Column(db.Enum(QuestionType), nullable=False)

    template_id = db.Column(db.Integer, db.ForeignKey("consentformtemplate.id"))
    template = db.relationship("ConsentFormTemplate", backref="consentformtemplatequestion")
