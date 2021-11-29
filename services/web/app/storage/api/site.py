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

from ...api import api
from ...api.responses import *
from ..api.building import delete_buildings_func

from flask import request, send_file
from ...decorators import token_required
from marshmallow import ValidationError

from ...database import db, SiteInformation, UserAccount, Sample, Building, Address

#from ..views import site_schema, new_site_schema, basic_site_schema, site_addresses_schema
from ..views import site_schema, site_addresses_schema
from ...misc.views import new_site_schema, basic_site_schema
from ...api.generics import *


@api.route("/storage/site/LIMBSITE-<id>", methods=["GET"])
@token_required
def site_view(id, tokenuser: UserAccount):

    return success_with_content_response(
        site_schema.dump(SiteInformation.query.filter_by(id=id).first_or_404())
    )

@api.route("/storage/site/LIMBSITE-<id>/addresses", methods=["GET"])
@token_required
def site_addresses_view(id, tokenuser: UserAccount):

    return success_with_content_response(
        site_addresses_schema.dump(SiteInformation.query.filter_by(id=id).first_or_404())
    )


@api.route("/storage/site/LIMBSITE-<id>/edit", methods=["PUT"])
@token_required
def storage_site_edit(id, tokenuser: UserAccount):
    values = request.get_json()
    print("values", values)
    site = SiteInformation.query.filter_by(id=id).first()
    if not site:
        return not_found("Site %s"%id)

    if site.is_locked:
        return locked_response("Site %s"%id)

    try:
        result = new_site_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    address_values = values.pop("address", None)
    site.update(values)

    if address_values:
        address = Address.query.filter_by(id=site.address_id).first()
        if address:
            address.update(address_values)
            address.editor_id = tokenuser.id
        else:
            address = Address(address_values)
            address.author_id = tokenuser.id

        db.session.add(address)
        try:
            db.session.flush()
            site.address_id = address.id
        except Exception as err:
            return transaction_error_response(err)

    db.session.add(site)
    try:
        db.session.commit()
        return success_with_content_response(basic_site_schema.dump(site))
    except Exception as err:
        return transaction_error_response(err)


@api.route("/storage/site/LIMBSITE-<id>/edit_addresses", methods=["POST"])
@token_required
def site_edit_addresses(id, tokenuser: UserAccount):
    values = request.get_json()
    print("values", values)
    new_address_id = values.pop("address_id", None)

    site = SiteInformation.query.filter_by(id=id).first()

    if not site:
        return not_found("Site %s"%id)

    if site.is_locked:
        return locked_response("Site %s"%id)

    new_values = values.pop("new_addresses", None)
    upd_values = values.pop("addresses", None)

    site.update(values)
    if new_address_id:
        # print("new addres", new_address_id)
        site.address_id = new_address_id

    db.session.add(site)

    if new_values:
        for avalues in new_values:
            deleted = avalues.pop("delete", None)
            is_default = avalues.pop("is_default", None)
            address_id = avalues.pop("id", None)

            if deleted:
                continue
            address = Address(**avalues)
            address.author_id = tokenuser.id
            db.session.add(address)

            if is_default:
                site.address_id = address.id


    try:
        db.session.flush()
    except Exception as err:
        return transaction_error_response(err)

    if upd_values:
        for avalues in upd_values:
            deleted = avalues.pop("delete", None)
            is_default = avalues.pop("is_default", None)
            address_id = avalues.pop("id", None)
            # print("address_id", address_id, "; delele", deleted)

            if address_id:
                # - Update address
                address = Address.query.filter_by(id=address_id).first()
                if not address:
                    return not_found("Address")

                if deleted is True:
                    db.session.delete(address)
                else:
                    address.update(avalues)
                    address.update({"editor_id": tokenuser.id})
                    db.session.add(address)


            if is_default:
                site.address_id = address.id

    site.update({"editor_id": tokenuser.id})
    db.session.add(site)

    try:
        db.session.commit()
        return success_with_content_response(basic_site_schema.dump(site))

    except Exception as err:
        return transaction_error_response(err)


# *
# Route for deleting a site.
# Includes validation for deleting.
# *
@api.route("/storage/site/LIMBSITE-<id>/delete", methods=["PUT"])
@token_required
def storage_site_delete(id, tokenuser: UserAccount):
    # Finds the site in the site table
    siteTableRecord = SiteInformation.query.filter_by(id=id).first()
    # Finds sample records which ref the site to delete and preserve foreign key integrity.
    sampleTableRecord = Sample.query.filter(Sample.site_id == id).all()

    if not siteTableRecord:
        return not_found()

    if siteTableRecord.is_locked:
        return locked_response()

    siteTableRecord.editor_id = tokenuser.id

    for record in sampleTableRecord:
        db.session.delete(record)
    try:
        db.session.flush()
        db.session.delete(siteTableRecord)
        db.session.commit()
        return success_without_content_response()
    except Exception as err:
        return transaction_error_response(err)


# *
# Function changes the state of the lock variable for the site.
# Locking a site reduces the functionality to the admin.
# *
@api.route("/storage/site/LIMBSITE-<id>/lock", methods=["PUT"])
@token_required
def storage_site_lock(id, tokenuser: UserAccount):

    site = SiteInformation.query.filter_by(id=id).first()

    if not site:
        return not_found()

    site.is_locked = not site.is_locked
    site.editor_id = tokenuser.id

    try:
        db.session.commit()
        db.session.flush()
        return success_with_content_response(site.is_locked)
    except Exception as err:
        return transaction_error_response(err)
