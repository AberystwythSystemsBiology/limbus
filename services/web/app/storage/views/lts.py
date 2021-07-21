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

from ...extensions import ma
import marshmallow_sqlalchemy as masql
from marshmallow import fields
from marshmallow_enum import EnumField
from ...database import ColdStorage, ColdStorageService, DocumentToColdStorage

from ..enums import (
    FixedColdStorageTemps,
    FixedColdStorageType,
    ColdStorageServiceResult,
    FixedColdStorageStatus,
)
from ..views.shelf import ColdStorageShelfSchema
from ...auth.views import BasicUserAccountSchema

from ...document.views import DocumentSchema


class DocumentToColdStorageSchema(masql.SQLAlchemySchema):
    class Meta:
        model = DocumentToColdStorage

    id = masql.auto_field()
    storage_id = masql.auto_field()
    document_id = masql.auto_field()
    author = ma.Nested(BasicUserAccountSchema)


document_to_cold_storage_schema = DocumentToColdStorageSchema()


class NewDocumentToColdStorageSchema(masql.SQLAlchemySchema):
    class Meta:
        model = DocumentToColdStorage

    storage_id = masql.auto_field()
    document_id = masql.auto_field()


new_document_to_cold_storage_schema = NewDocumentToColdStorageSchema()


class ColdStorageServiceSchema(masql.SQLAlchemySchema):
    class Meta:
        model = ColdStorageService

    id = masql.auto_field()
    date = masql.auto_field()
    conducted_by = masql.auto_field()
    status = EnumField(ColdStorageServiceResult, by_value=True)
    comments = masql.auto_field()
    temp = masql.auto_field()


cold_storage_service_schema = ColdStorageServiceSchema()
cold_storage_services_schema = ColdStorageServiceSchema(many=True)


class NewColdStorageServiceSchema(masql.SQLAlchemySchema):
    class Meta:
        model = ColdStorageService

    date = masql.auto_field()
    conducted_by = masql.auto_field()
    status = EnumField(ColdStorageServiceResult)
    comments = masql.auto_field()
    storage_id = masql.auto_field()
    temp = masql.auto_field()


new_cold_storage_service_schema = NewColdStorageServiceSchema()


class BasicColdStorageSchema(masql.SQLAlchemySchema):
    class Meta:
        model = ColdStorage

    id = masql.auto_field()
    alias = masql.auto_field()
    uuid = masql.auto_field()
    serial_number = masql.auto_field()
    manufacturer = masql.auto_field()
    temp = EnumField(FixedColdStorageTemps, by_value=True)
    type = EnumField(FixedColdStorageType, by_value=True)
    status = EnumField(FixedColdStorageStatus, by_value=True)


basic_cold_storage_schema = BasicColdStorageSchema()
basic_cold_storages_schema = BasicColdStorageSchema(many=True)


class ColdStorageSchema(masql.SQLAlchemySchema):
    class Meta:
        model = ColdStorage

    id = masql.auto_field()
    alias = masql.auto_field()
    is_locked = masql.auto_field()
    uuid = masql.auto_field()
    serial_number = masql.auto_field()
    manufacturer = masql.auto_field()
    temp = EnumField(FixedColdStorageTemps, by_value=True)
    type = EnumField(FixedColdStorageType, by_value=True)
    room_id = masql.auto_field()
    shelves = ma.Nested(ColdStorageShelfSchema, many=True)
    author = ma.Nested(BasicUserAccountSchema)
    created_on = ma.Date()
    status = EnumField(FixedColdStorageStatus, by_value=True)
    service_history = ma.Nested(ColdStorageServiceSchema, many=True)
    documents = ma.Nested(DocumentSchema(), many=True)
    # room = ma.Nested(BasicRoomSchema, many=False)


cold_storage_schema = ColdStorageSchema()


class NewColdStorageSchema(masql.SQLAlchemySchema):
    class Meta:
        model = ColdStorage

    alias = masql.auto_field()
    is_locked = masql.auto_field()
    serial_number = masql.auto_field()
    manufacturer = masql.auto_field()
    comments = masql.auto_field()
    temp = EnumField(FixedColdStorageTemps)
    type = EnumField(FixedColdStorageType)
    room_id = masql.auto_field()
    status = EnumField(FixedColdStorageStatus)


new_cold_storage_schema = NewColdStorageSchema()
