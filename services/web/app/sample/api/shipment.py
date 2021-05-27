# Copyright (C) 2021  Keiron O'Shea <keo7@aber.ac.uk>
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


from flask import request, abort, url_for
from marshmallow import ValidationError
from ...api import api, generics
import requests
import json
from ...api.responses import *
from ...decorators import token_required
from ...misc import get_internal_api_header
from ...database import db, UserCart, UserAccount
from ..views import user_cart_samples_schema, new_cart_sample_schema

@api.route("/cart", methods=["GET"])
@token_required
def get_cart(tokenuser: UserAccount):
    cart = UserCart.query.filter_by(author_id = tokenuser.id).all()
    return success_with_content_response(user_cart_samples_schema.dump(cart))

@api.route("/cart/remove/<uuid>", methods=["DELETE"])
@token_required
def remove_sample_from_cart(uuid: str, tokenuser: UserAccount):
    sample_response = requests.get(
        url_for("api.sample_view_sample", uuid=uuid, _external=True),
        headers=get_internal_api_header(tokenuser),
    )

    if sample_response.status_code == 200:
        sample_id = sample_response.json()["content"]["id"]

        uc = UserCart.query.filter_by(author_id = tokenuser.id, sample_id = sample_id).first()

        if uc:
            db.session.delete(uc)
            db.session.commit()
                
            return success_with_content_response({"msg": "%s removed from cart" % (uuid)})
        else:
            return success_with_content_response({"msg": "%s not in user cart" % (uuid)})

    else:
        return sample_response.content


@api.route("/cart/add/<uuid>", methods=["POST"])
@token_required
def add_sample_to_cart(uuid: str, tokenuser: UserAccount):
    sample_response = requests.get(
        url_for("api.sample_view_sample", uuid=uuid, _external=True),
        headers=get_internal_api_header(tokenuser),
    )

    if sample_response.status_code == 200:
        sample_id = sample_response.json()["content"]["id"]
        try:
            cart_sample_schema = new_cart_sample_schema.load(
                {"sample_id": sample_id}
                )
            
        except ValidationError as err:
            return validation_error_response(err)

        check = UserCart.query.filter_by(author_id = tokenuser.id, sample_id = sample_id).first()
        
        if check != None:
            return success_with_content_response({"msg": "Sample already added to Cart"})


        new_uc = UserCart(
                sample_id = sample_id,
                author_id = tokenuser.id
        )

        try:
            db.session.add(new_uc)
            db.session.commit()
            db.session.flush()

            return success_with_content_response({"msg": "Sample added to Cart"})

        except Exception as err:
            return transaction_error_response(err)
    else:
        return sample_response.content

