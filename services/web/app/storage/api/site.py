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

@api.route("/misc/site/LIMBSITE-<id>", methods=["GET"])
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

@api.route("/storage/site/LIMBSITE-<id>/delete", methods=["PUT"])
@token_required
def storage_site_delete(id, tokenuser: UserAccount):
    siteTableRecord = SiteInformation.query.filter_by(id=id).first()
    sampleTableRecord = Sample.query.filter(Sample.site_id==id).all()


    if not siteTableRecord:
        return not_found()

    if siteTableRecord.is_locked:
        return locked()

    siteTableRecord.editor_id = tokenuser.id

    for record in sampleTableRecord:
        db.session.delete(record)

    attachedBuildings = Building.query.filter(Building.site_id==id).all()
    for building in attachedBuildings:
        if delete_buildings_func(building) == 400:
            return sample_assigned_delete_response()

    db.session.commit()
    db.session.delete(siteTableRecord)
    db.session.commit()
    return success_without_content_response()


