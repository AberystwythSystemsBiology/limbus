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
from flask import request, abort, url_for
from marshmallow import ValidationError
from ...api import api, generics
from ...api.responses import *
from ...decorators import token_required
from ...misc import get_internal_api_header
from ...database import db, UserCart, UserAccount
from ..views import user_cart_samples_schema

@api.route("/cart", methods=["GET"])
@token_required
def get_cart(tokenuser: UserAccount):
    cart = UserCart.query.filter_by(author_id = tokenuser.id).all()
    return success_with_content_response(user_cart_samples_schema.dump(cart))
