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

from ...database import SampleRack, EntityToStorage, ColdStorageShelf
from ...sample.views import BasicSampleSchema
from ...sample.enums import Colour
from ...auth.views import BasicUserAccountSchema


class ViewSampleToSampleRackSchema(masql.SQLAlchemySchema):
    class Meta:
        model = EntityToStorage

    id = masql.auto_field()
    sample_id = masql.auto_field()
    rack_id = masql.auto_field()
    row = masql.auto_field()
    col = masql.auto_field()
    entry = masql.auto_field()
    entry_datetime = masql.auto_field()

    sample = ma.Nested(BasicSampleSchema)


view_sample_to_sample_rack_schema = ViewSampleToSampleRackSchema()


class NewSampleToSampleRackSchema(masql.SQLAlchemySchema):
    class Meta:
        model = EntityToStorage

    sample_id = masql.auto_field()
    rack_id = masql.auto_field()
    row = masql.auto_field()
    col = masql.auto_field()
    entry = masql.auto_field()
    entry_datetime = masql.auto_field()


new_sample_to_sample_rack_schema = NewSampleToSampleRackSchema()


class ShelfViewSchema(masql.SQLAlchemySchema):
    class Meta:
        model = ColdStorageShelf

    id = masql.auto_field()
    name = masql.auto_field()

    _links = ma.Hyperlinks(
        {"self": ma.URLFor("storage.view_shelf", id="<id>", _external=True)}
    )


class SampleRackSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleRack

    id = masql.auto_field()
    uuid = masql.auto_field()
    description = masql.auto_field()
    serial_number = masql.auto_field()
    num_rows = masql.auto_field()
    num_cols = masql.auto_field()
    colour = EnumField(Colour, by_value=True)
    author = ma.Nested(BasicUserAccountSchema)
    created_on = ma.Date()
    entity_to_storage_instances = ma.Nested(ViewSampleToSampleRackSchema, many=True)
    shelf = ma.Nested(ShelfViewSchema)

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("storage.view_rack", id="<id>", _external=True),
            "collection": ma.URLFor("storage.rack_index", _external=True),
            "qr_code": ma.URLFor(
                "sample.view_barcode", uuid="<uuid>", t="qrcode", _external=True
            ),
            "assign_sample": ma.URLFor(
                "storage.assign_rack_sample",
                id="<id>",
                row="rph",
                column="cph",
                _external=True,
            ),
        }
    )


rack_schema = SampleRackSchema()


class BasicSampleRackSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleRack

    id = masql.auto_field()
    uuid = masql.auto_field()
    serial_number = masql.auto_field()
    num_rows = masql.auto_field()
    num_cols = masql.auto_field()
    colour = EnumField(Colour, by_value=True)
    author = ma.Nested(BasicUserAccountSchema)
    created_on = ma.Date()

    # entity_to_storage_instances = ma.Method(deserialize="_sample_count")

    sample_count = ma.Function(lambda obj: len(obj.entity_to_storage_instances))

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("storage.view_rack", id="<id>", _external=True),
            "collection": ma.URLFor("storage.rack_index", _external=True),
            "qr_code": ma.URLFor(
                "sample.view_barcode", uuid="<uuid>", t="qrcode", _external=True
            ),
        }
    )

    def _sample_count(self, obj):
        return len(obj.views)


basic_sample_rack_schema = BasicSampleRackSchema()
basic_sample_racks_schema = BasicSampleRackSchema(many=True)


class NewSampleRackSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleRack

    description = masql.auto_field()
    serial_number = masql.auto_field()
    num_rows = masql.auto_field()
    num_cols = masql.auto_field()
    colour = EnumField(Colour)


new_sample_rack_schema = NewSampleRackSchema()
