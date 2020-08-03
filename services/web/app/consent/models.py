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


class ConsentFormTemplate(db.Model):
    __tablename__ = "consent_form_templates"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)

    version = db.Column(db.String(64))

    upload_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

    uploader = db.Column(db.Integer, db.ForeignKey("users.id"))


class ConsentFormTemplateQuestion(db.Model):
    __tablename__ = "consent_form_template_questions"

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String, nullable=False)

    template_id = db.Column(db.Integer, db.ForeignKey("consent_form_templates.id"))

    upload_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )
    uploader = db.Column(db.Integer, db.ForeignKey("users.id"))
