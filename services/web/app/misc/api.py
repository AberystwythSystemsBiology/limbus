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
from ..database import *

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

from flask import request, send_file, jsonify, abort
from ..decorators import token_required
from marshmallow import ValidationError

import treepoem
from io import BytesIO
from random import choice
import base64


@api.route("/misc/barcode", methods=["POST"])
def misc_generate_barcode():

    values = request.get_json()

    img = treepoem.generate_barcode(barcode_type=values["type"], data=values["data"])

    img_io = BytesIO()
    img.save(img_io, format="PNG")
    img_io.seek(0)

    return {"success": True, "b64": base64.b64encode(img_io.getvalue()).decode()}, 200


@api.route("/misc/greeting", methods=["GET"])
def get_greeting():

    dictionary = {
        "Hello": "English",
        "Rite butt?": "the South Wales Valleys",
        "ghaH 'ej Duvan": "Klingon",
        "Ay 'up mi duck?": "Staffordshire",
        "'Allo, 'Allo": "London Policeman",
        "Witaj": "Polish",
        "Salaam": "Arabic",
        "Bonjour": "French",
        "God dag": "Danish",
        "Yasou": "Greek",
        "Shalom": "Hebrew",
        "Namaste": "Hindi",
        "Salve": "Italian",
        "Konnichiwa": "Japanese",
        "Hola": "Spanish",
        "Selamat datang": "Malaysian",
        "Guten Tag": "German",
        "Merhaba": "Turkish",
        "Helo": "Welsh",
        "Hala": "Arabic",
        "Zdravo": "Serbian",
        "Nei ho": "Cantonese",
        "Dobrý den": "Czech",
        "Mingalaba": "Burmese",
        "Labdien": "Latvian",
    }

    c = choice(list(dictionary.keys()))

    return jsonify({"language": dictionary[c], "greeting": c})


@api.route("/misc/panel", methods=["GET"])
@token_required
def get_data(tokenuser: UserAccount):
    # .strftime("%Y:%m:%d")

    """
    a = db.session.query(
        func.date_trunc("day", Sample.created_on)).group_by(func.date_trunc("day", Sample.created_on)).all()


    """

    data = {
        "name": SiteInformation.query.filter_by(is_external=False).order_by(SiteInformation.id).first().name,
        "basic_statistics": {
            "sample_count": Sample.query.filter(Sample.remaining_quantity>0).count(),
            "user_count": UserAccount.query.count(),
            "site_count": SiteInformation.query.filter_by(is_external=False).count(),
            "donor_count": Donor.query.count(),
        },
        "donor_statistics": {
            "donor_status": prepare_for_chart_js(
                [
                    (type.value, count)
                    for (type, count) in db.session.query(
                        Donor.status, func.count(Donor.status)
                    )
                    .group_by(Donor.status)
                    .all()
                ]
            ),
            "donor_sex": prepare_for_chart_js(
                [
                    (type.value, count)
                    for (type, count) in db.session.query(
                        Donor.sex, func.count(Donor.sex)
                    )
                    .group_by(Donor.sex)
                    .all()
                ]
            ),
            "donor_race": prepare_for_chart_js(
                [
                    (type.value, count)
                    for (type, count) in db.session.query(
                        Donor.race, func.count(Donor.race)
                    )
                    .group_by(Donor.race)
                    .all()
                ]
            ),
        },
        "sample_statistics": {
            "added_time": prepare_for_chart_js(
                [
                    (date.strftime("%Y-%m-%d"), count)
                    for (date, count) in db.session.query(
                        func.date_trunc("day", Sample.created_on), func.count(Sample.id)
                    )
                    .group_by(func.date_trunc("day", Sample.created_on))
                    .all()
                ]
            ),
            "sample_type": prepare_for_chart_js(
                [
                    (type.value, count)
                    for (type, count) in db.session.query(
                        Sample.base_type, func.count(Sample.base_type)
                    )
                    .group_by(Sample.base_type)
                    .all()
                ]
            ),
            "sample_biohazard": prepare_for_chart_js(
                [
                    (type.value, count)
                    for (type, count) in db.session.query(
                        Sample.biohazard_level, func.count(Sample.biohazard_level)
                    )
                    .group_by(Sample.biohazard_level)
                    .all()
                ]
            ),
            "sample_source": prepare_for_chart_js(
                [
                    (type.value, count)
                    for (type, count) in db.session.query(
                        Sample.source, func.count(Sample.source)
                    )
                    .group_by(Sample.source)
                    .all()
                ]
            ),  # SampleSource
            "sample_status": prepare_for_chart_js(
                [
                    (type.value, count)
                    for (type, count) in db.session.query(
                        Sample.status, func.count(Sample.status)
                    )
                    .group_by(Sample.status)
                    .all()
                ]
            ),  # SampleSource
        },
        "storage_statistics": {},
        "attribute_statistics": {
            "attribute_type": prepare_for_chart_js(
                [
                    (type.value, count)
                    for (type, count) in db.session.query(
                        Attribute.type, func.count(Attribute.type)
                    )
                    .group_by(Attribute.type)
                    .all()
                ]
            )
        },
        "protocol_statistics": {
            "protocol_type": prepare_for_chart_js(
                [
                    (type.value, count)
                    for (type, count) in db.session.query(
                        ProtocolTemplate.type, func.count(ProtocolTemplate.type)
                    )
                    .group_by(ProtocolTemplate.type)
                    .all()
                ]
            )
        },
        "document_statistics": {
            "document_type": prepare_for_chart_js(
                [
                    (type.value, count)
                    for (type, count) in db.session.query(
                        Document.type, func.count(Document.type)
                    )
                    .group_by(Document.type)
                    .all()
                ]
            )
        },
    }

    return success_with_content_response(data)


@api.route("/misc/site/external", methods=["GET"])
@token_required
def site_external_home(tokenuser: UserAccount):
    return success_with_content_response(
        basic_sites_schema.dump(SiteInformation.query.filter_by(is_external=True).all())
    )


@api.route("/misc/site", methods=["GET"])
@token_required
def site_home(tokenuser: UserAccount):
    return success_with_content_response(
        basic_sites_schema.dump(SiteInformation.query.filter_by(is_external=False).all())
    )


@api.route("/misc/site/tokenuser", methods=["GET"])
@token_required
def site_home_tokenuser(tokenuser: UserAccount):

    if tokenuser.is_admin:
        sites = basic_sites_schema.dump(SiteInformation.query.filter_by(is_external=False).all())

    else:
        sites = basic_sites_schema.dump(
            SiteInformation.query.filter_by(is_external=False, id=tokenuser.site_id).all()
        )

    choices = []
    settings = tokenuser.settings

    try:
        id0 = settings["data_entry"]["site"]["default"]
        nm0 = None
    except:
        id0 = None

    try:
        choices0 = settings["data_entry"]["site"]["choices"]
        if len(choices0) ==  0:
            choices0 = None
    except:
        choices0 = None

    for site in sites:
        if choices0:
            if site["id"] not in choices0:
                continue

        if id0 and site["id"] == id0:
            nm0 = "<%s>%s - %s" % (site["id"], site["name"], site["description"])
            continue

        choices.append(
            (
                site["id"],
                "<%s>%s - %s" % (site["id"], site["name"], site["description"])
            )
        )

    if id0 and  nm0:
        # -- Insert default
        choices = [(id0, nm0)] + choices

    # print({'site_info': sites, 'choices': choices, 'user_site_id': tokenuser.site_id})
    return success_with_content_response({'site_info': sites, 'choices': choices, 'user_site_id': tokenuser.site_id})


@api.route("/misc/site/LIMBSIT-<id>", methods=["GET"])
@token_required
def site_view_site(id: id, tokenuser: UserAccount):
    site = SiteInformation.query.filter_by(id=id).first()

    if site:
        return success_with_content_response(basic_site_schema.dump(site))
    else:
        return abort(404)


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