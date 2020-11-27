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
from ...database import (
    SiteInformation,
    Building,
    Room,
    ColdStorage,
    ColdStorageShelf,
    EntityToStorage,
)
from ..enums import FixedColdStorageType, FixedColdStorageTemps
from flask import url_for


class NewSampleToShelfSchema(masql.SQLAlchemySchema):
    class Meta:
        model = EntityToStorage

    sample_id = masql.auto_field()
    shelf_id = masql.auto_field()
    entry_datetime = masql.auto_field()
    entry = masql.auto_field()


new_sample_to_shelf_schema = NewSampleToShelfSchema()
new_samples_to_shelves_schema = NewSampleToShelfSchema(many=True)


class NewSampleToSampleRackSchema(masql.SQLAlchemySchema):
    class Meta:
        model = EntityToStorage

    sample_id = masql.auto_field()
    rack_id = masql.auto_field()
    entry_datetime = masql.auto_field()
    entry = masql.auto_field()


new_sample_to_sample_rack_schema = NewSampleToSampleRackSchema()
new_samples_to_sample_racks_schema = NewSampleToSampleRackSchema(many=True)


class NewSampleRackToShelfSchema(masql.SQLAlchemySchema):
    class Meta:
        model = EntityToStorage

    rack_id = masql.auto_field()
    shelf_id = masql.auto_field()
    entry_datetime = masql.auto_field()
    entry = masql.auto_field()


new_sample_rack_to_shelf_schema = NewSampleRackToShelfSchema()
new_sample_racks_to_shelves_schema = NewSampleRackToShelfSchema(many=True)


class TreeShelfSchema(masql.SQLAlchemySchema):
    class Meta:
        model = ColdStorageShelf

    id = masql.auto_field()
    name = masql.auto_field()

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("storage.view_shelf", id="<id>", _external=True),
        }
    )


class TreeColdStorageSchema(masql.SQLAlchemySchema):
    class Meta:
        model = ColdStorage

    id = masql.auto_field()
    manufacturer = masql.auto_field()
    temp = EnumField(FixedColdStorageTemps, by_value=True)
    type = EnumField(FixedColdStorageType, by_value=True)

    shelves = ma.Nested(TreeShelfSchema, many=True)

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("storage.view_cold_storage", id="<id>", _external=True),
        }
    )


class TreeRoomSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Room

    id = masql.auto_field()
    name = masql.auto_field()
    storage = ma.Nested(TreeColdStorageSchema, many=True)

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("storage.view_room", id="<id>", _external=True),
        }
    )


class TreeBuildingSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Building

    id = masql.auto_field()
    name = masql.auto_field()
    rooms = ma.Nested(TreeRoomSchema, many=True)

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("storage.view_building", id="<id>", _external=True),
        }
    )


class TreeSiteSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SiteInformation

    id = masql.auto_field()
    name = masql.auto_field()
    buildings = ma.Nested(TreeBuildingSchema, many=True)

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("storage.view_site", id="<id>", _external=True),
        }
    )


tree_sites_schema = TreeSiteSchema(many=True)
