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

from ...database import db,SiteInformation, UserAccount,Sample,Building

from ..views import site_schema, new_site_schema, basic_site_schema
from ...api.generics import *

@api.route("/storage/site/LIMBSITE-<id>", methods=["GET"])
@token_required
def site_view(id, tokenuser: UserAccount):

    return success_with_content_response(
        site_schema.dump(SiteInformation.query.filter_by(id=id).first_or_404())
    )

@api.route("/storage/site/LIMBSITE-<id>/edit", methods=["PUT"])
@token_required
def storage_site_edit(id, tokenuser: UserAccount):

    values = request.get_json()

    return generic_edit(
        db, SiteInformation, id, new_site_schema, basic_site_schema, values, tokenuser
    )

#*
# Route for deleting a site.
# Includes validation for deleting.
#*
@api.route("/storage/site/LIMBSITE-<id>/delete", methods=["PUT"])
@token_required
def storage_site_delete(id, tokenuser: UserAccount):
    # Finds the site in the site table
    siteTableRecord = SiteInformation.query.filter_by(id=id).first()
    # Finds sample records which ref the site to delete and preserve foreign key integrity.
    sampleTableRecord = Sample.query.filter(Sample.site_id==id).all()


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

#*
# Function changes the state of the lock variable for the site.
# Locking a site reduces the functionality to the admin.
#*
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



