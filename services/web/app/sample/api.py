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


from flask import request, abort

from marshmallow import ValidationError

from ..api import api
from ..api.responses import *
from ..decorators import token_required
from ..database import (
    db,
    UserAccount,
    Sample,
    SampleConsent,
    SampleConsentAnswer,
    SampleProtocolEvent
)

from .views import (
    basic_samples_schema,
    new_consent_schema,
    consent_schema,
    new_consent_answer_schema,
    new_sample_protocol_event_schema,
    sample_protocol_event_schema,
    new_sample_schema

)

import datetime


@api.route("/sample", methods=["GET"])
@token_required
def sample_home(tokenuser: UserAccount):
    return success_with_content_response(
        basic_samples_schema.dump(Sample.query.filter_by().all())
    )

