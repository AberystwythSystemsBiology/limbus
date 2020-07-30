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
from .enums import ProtocolSampleType, ProtocolUploadTypes, ProtocolTypes


class ProcessingTemplate(db.Model):
    __tablename__ = "processing_templates"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(128))
    type = db.Column(db.Enum(ProtocolTypes))

    sample_type = db.Column(db.Enum(ProtocolSampleType))

    upload_type = db.Column(db.Enum(ProtocolUploadTypes))

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    # has_template = db.Column(db.Boolean)
    has_document = db.Column(db.Boolean)

    upload_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )


class ProcessingTemplateToDocument(db.Model):
    __tablename__ = "processing_templates_to_documents"

    id = db.Column(db.Integer, primary_key=True)

    template_id = db.Column(db.Integer, db.ForeignKey("processing_templates.id"))
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id"))

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    upload_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )
