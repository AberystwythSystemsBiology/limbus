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


from sqlalchemy import func
from ..database import db, Address, SiteInformation, UserAccount, Sample

from ..api import api
from ..api.responses import *

from .views import (
    new_address_schema,
    new_site_schema,
    basic_address_schema,
    basic_addresses_schema,
    basic_site_schema,
    basic_sites_schema,
)

from flask import request
from ..decorators import token_required
from marshmallow import ValidationError


@api.route("/misc/panel", methods=["GET"])
@token_required
def get_panel_data():
    data = {
        "name": SiteInformation.query.first().name,
        "basic_statistics": {
            "sample_count": Sample.query.count(),
            "user_count": UserAccount.query.count(),
            "site_count": SiteInformation.query.count(),
            "donor_count": 0,
        },
        "sample_statistics": {
            "sample_type":[(type.value, count) for (type, count) in db.session.query(Sample.type, func.count(Sample.type)).group_by(Sample.type).all()],
            "saple_biohazard": [(type.value, count) for (type, count) in db.session.query(Sample.biohazard_level, func.count(Sample.biohazard_level)).group_by(Sample.biohazard_level).all()],
            "sample_source":  [(type.value, count) for (type, count) in db.session.query(Sample.source, func.count(Sample.source)).group_by(Sample.source).all()],  # SampleSource
            "sample_status":  [(type.value, count) for (type, count) in db.session.query(Sample.status, func.count(Sample.status)).group_by(Sample.status).all()],  # SampleSource

        },
    }
    return success_with_content_response(data)


@api.route("/misc/site", methods=["GET"])
@token_required
def site_home(tokenuser: UserAccount):
    return success_with_content_response(
        basic_sites_schema.dump(SiteInformation.query.all())
    )


@api.route("/misc/address/", methods=["GET"])
@token_required
def address_home(tokenuser: UserAccount):
    return success_with_content_response(
        basic_addresses_schema.dump(Address.query.all())
    )


@api.route("/misc/address/new", methods=["POST"])
@token_required
def misc_new_address(tokenuser: UserAccount):
    values = request.get_json()

    if values is None:
        return no_values_response()
    try:
        result = new_address_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    new_address = Address(**result)
    new_address.author_id = tokenuser.id

    try:
        db.session.add(new_address)
        db.session.commit()
        db.session.flush()
        return success_with_content_response(basic_address_schema.dumps(new_address))
    except Exception as err:
        return transaction_error_response(err)


@api.route("/misc/site/new", methods=["POST"])
@token_required
def misc_new_site(tokenuser: UserAccount):
    values = request.get_json()

    if values is None:
        return no_values_response()

    try:
        result = new_site_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    new_site = SiteInformation(**result)
    new_site.author_id = tokenuser.id

    try:
        db.session.add(new_site)
        db.session.commit()
        db.session.flush()
        return success_with_content_response(basic_site_schema.dumps(new_site))
    except Exception as err:
        return transaction_error_response(err)
