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

from .models import (
    CustomAttributes,
    CustomAttributeOption,
    CustomAttributeTextSetting,
    CustomAttributeNumericSetting,
)
from ..auth.views import UserView
from .. import db


def CustomAttributesIndexView() -> dict:
    """
        This method returns an dictionary of information concerning attributes, as well as their author information.
    """
    attributes = db.session.query(CustomAttributes).all()

    data = {}

    for attribute in attributes:

        data[attribute.id] = {
            "term": attribute.term,
            "description": attribute.description,
            "type": attribute.type.value,
            "accession": attribute.accession,
            "ref": attribute.ref,
            "element": attribute.element.value,
            "required": attribute.required,
            "creation_date": attribute.creation_date,
            "user_information": UserView(attribute.author_id),
        }

    return data


def CustomAttributeView(ca_id) -> dict:

    attribute = (
        db.session.query(CustomAttributes)
        .filter(CustomAttributes.id == ca_id)
        .first_or_404()
    )

    data = {
        "id": attribute.id,
        "term": attribute.term,
        "description": attribute.description,
        "type": attribute.type.value,
        "accession": attribute.accession,
        "ref": attribute.ref,
        "element": attribute.element.value,
        "required": attribute.required,
        "creation_date": attribute.creation_date,
        "user_information": UserView(attribute.author_id),
    }

    if data["type"] == "Option":
        options = (
            db.session.query(CustomAttributeOption)
            .filter(CustomAttributeOption.custom_attribute_id == attribute.id)
            .all()
        )

        o_data = {}

        for option in options:
            o_data[option.id] = {
                "term": option.term,
                "accession": option.accession,
                "ref": option.ref,
            }

        data["option_info"] = o_data

    elif data["type"] == "Numeric":

        settings = (
            db.session.query(CustomAttributeNumericSetting)
            .filter(CustomAttributeNumericSetting.custom_attribute_id == attribute.id)
            .first_or_404()
        )

        data["numeric_settings"] = {
            "id": settings.id,
            "measurement": settings.measurement,
            "prefix": settings.prefix,
        }

    else:

        settings = (
            db.session.query(CustomAttributeTextSetting)
            .filter(CustomAttributeTextSetting.custom_attribute_id == attribute.id)
            .first_or_404()
        )

        data["text_settings"] = {"id": settings.id, "max_length": settings.max_length}

    return data
