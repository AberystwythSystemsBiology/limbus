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

from .. import db, ma
from .models import ConsentFormTemplate, ConsentFormTemplateQuestion
from .enums import QuestionType

import marshmallow_sqlalchemy as masql
from marshmallow import fields
from marshmallow_enum import EnumField

from ..auth.views import BasicUserAccountSchema

class NewConsentFormTemplateSchema(masql.SQLAlchemySchema):
    class Meta:
        model = ConsentFormTemplate

    name = masql.auto_field()
    version = masql.auto_field()
    description = masql.auto_field()

new_consent_form_template_schema = NewConsentFormTemplateSchema()
new_consent_form_templates_schema = NewConsentFormTemplateSchema(many=True)

class NewConsentFormQuestionSchema(masql.SQLAlchemySchema):
    class Meta:
        model = ConsentFormTemplateQuestion

    question = masql.auto_field()
    type = EnumField(QuestionType)

new_consent_form_question_schema = NewConsentFormQuestionSchema()

class BasicConsentFormTemplateSchema(masql.SQLAlchemySchema):
    class Meta:
        model = ConsentFormTemplate

    id = masql.auto_field()
    name = masql.auto_field()
    version = masql.auto_field()
    created_on = fields.Date()
    author = ma.Nested(BasicUserAccountSchema)

basic_consent_form_template_schema = BasicConsentFormTemplateSchema()
basic_consent_form_templates_schema = BasicConsentFormTemplateSchema(many=True)


class BasicConsentFormQuestionSchema(masql.SQLAlchemySchema):
    class Meta:
        model= ConsentFormTemplateQuestion

    id = masql.auto_field()
    question = masql.auto_field()
    type = EnumField(QuestionType)
    author = ma.Nested(BasicUserAccountSchema)

basic_consent_form_question_schema = BasicConsentFormQuestionSchema()
basic_consent_form_questions_schema = BasicConsentFormQuestionSchema(many=True)


class ConsentFormTemplateSchema(masql.SQLAlchemySchema):
    class Meta:
        model = ConsentFormTemplate

    id = masql.auto_field()
    name = masql.auto_field()
    description = masql.auto_field()
    version = masql.auto_field()
    created_on = fields.Date()
    author = ma.Nested(BasicUserAccountSchema)
    questions = ma.Nested(BasicConsentFormQuestionSchema(many=True))

consent_form_template_schema = ConsentFormTemplateSchema()
consent_form_templates_schema = ConsentFormTemplateSchema(many=True)

