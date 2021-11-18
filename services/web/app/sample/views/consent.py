# Copyright (C) 2020  Keiron O'Shea <keo7@aber.ac.uk>
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
from ...database import SampleConsent, SampleConsentAnswer

import marshmallow_sqlalchemy as masql

from ...consent.views import (
    BasicConsentFormQuestionSchema,
    BasicConsentFormTemplateSchema,
)
from ..views.protocol import DonorProtocolEventSchema, BasicDonorProtocolEventSchema
from ...auth.views import BasicUserAccountSchema, UserAccountSearchSchema

class NewConsentSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleConsent

    identifier = masql.auto_field()
    donor_id = masql.auto_field()
    comments = masql.auto_field()
    undertaken_by = masql.auto_field()
    template_id = masql.auto_field()
    date = masql.auto_field()


new_consent_schema = NewConsentSchema()


class BasicConsentSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleConsent

    id = masql.auto_field()
    identifier = masql.auto_field()
    donor_id = masql.auto_field()
    withdrawn = masql.auto_field()
    withdrawal_date = ma.Date()
    study = ma.Nested(BasicDonorProtocolEventSchema, many=False)

basic_consent_schema = BasicConsentSchema()

class ConsentSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleConsent

    id = masql.auto_field()
    identifier = masql.auto_field()
    donor_id = masql.auto_field()

    comments = masql.auto_field()
    undertaken_by = masql.auto_field()
    template = ma.Nested(BasicConsentFormTemplateSchema, many=False)
    template_questions = ma.Nested(BasicConsentFormQuestionSchema, many=True)
    #author = ma.Nested(BasicUserAccountSchema, many=False)
    author = ma.Nested(UserAccountSearchSchema, many=False)
    created_on = ma.Date()
    date = ma.Date()
    answers = ma.Nested(BasicConsentFormQuestionSchema, many=True)
    withdrawn = masql.auto_field()
    withdrawal_date = ma.Date()
    study = ma.Nested(DonorProtocolEventSchema, many=False)
    _links = ma.Hyperlinks(
        {
            "edit": ma.URLFor("donor.edit_donor_consent", id="<id>", donor_id="<donor_id>", _external=True),
            "remove": ma.URLFor("donor.remove_donor_consent", id="<id>", _external=True)
        })


consent_schema = ConsentSchema()


class NewConsentAnswerSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleConsentAnswer

    consent_id = masql.auto_field()
    question_id = masql.auto_field()


new_consent_answer_schema = NewConsentAnswerSchema()
new_consent_answers_schema = NewConsentAnswerSchema(many=True)
