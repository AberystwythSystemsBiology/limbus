# Copyright (C) 2019-2021  Keiron O'Shea <keo7@aber.ac.uk>
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

from flask_wtf import FlaskForm
from wtforms import (
    PasswordField,
    StringField,
    SubmitField,
    ValidationError,
    SelectField,
    BooleanField,
    FormField,
    SelectField,
    SelectMultipleField
)
from wtforms.validators import DataRequired, Email, EqualTo
from ...validators import validate_against_text

from ...auth.enums import Title, AccountType


from ...auth.models import UserAccount

from ...sample.enums import SampleBaseType, FluidSampleType, \
                    ContainerBaseType, FluidContainer, CellContainer



class UserAccountRegistrationForm(FlaskForm):

    title = SelectField("Title", validators=[DataRequired()], choices=Title.choices())

    first_name = StringField("First Name", validators=[DataRequired()])
    middle_name = StringField("Middle Name")
    last_name = StringField("Last Name", validators=[DataRequired()])

    email = StringField(
        "Email Address",
        description="We'll never share your email with anyone else.",
        validators=[DataRequired(), Email()],
    )

    password = PasswordField(
        "Password",
        description="Please ensure that you provide a secure password",
        validators=[
            DataRequired(),
            EqualTo("confirm_password", message="Passwords must match"),
        ],
    )

    is_admin = BooleanField("Is Admin?")

    confirm_password = PasswordField("Confirm Password")

    submit = SubmitField("Register")

    def validate_email(self, field):
        if UserAccount.query.filter_by(email=field.data).first():
            raise ValidationError("Email address already in use.")


def AccountLockForm(email):
    class StaticForm(FlaskForm):
        submit = SubmitField("Submit")

    setattr(
        StaticForm,
        "email",
        StringField(
            "Please enter %s" % (email),
            [DataRequired(), validate_against_text(email)],
        ),
    )

    return StaticForm()


def AdminUserAccountEditForm(sites=[], data={})->FlaskForm:
    class StaticForm(FlaskForm):
        title = SelectField("Title", validators=[DataRequired()], choices=Title.choices())

        first_name = StringField("First Name", validators=[DataRequired()])
        middle_name = StringField("Middle Name")
        last_name = StringField("Last Name", validators=[DataRequired()])

        email = StringField(
            "Email Address",
            description="We'll never share your email with anyone else.",
            validators=[DataRequired(), Email()],
        )
        site_id = SelectField(
            "Affiliated Site",
            coerce=int,
            choices=sites,
        )


        # is_admin = BooleanField("Is Admin?")

        account_type = SelectField("Account Type",
                                   validators=[DataRequired()], choices=AccountType.choices())

        #data_entry = FormField("UserSettings")
        # viewing = FormField("UserSettings")

        submit = SubmitField("Register")

        # def validate_email(self, field):
        #     if UserAccount.query.filter_by(email=field.data).first():
        #         raise ValidationError("Email address already in use.")

    return StaticForm(data=data)


class UserSettings(FlaskForm):

    site_default = StringField("Default working site")
    site_choices = SelectMultipleField(
            "Consent type", choices=[]) #sites)
    #
    # consent_template_default = StringField("Default working consent template")
    # consent_template_choices = SelectMultipleField(
    #         "Consent template choices", choices=[]) #=consent_templates),
    #
    # study_protocol_default = StringField("Default project/study protocol")#, choices=stu_protocols)
    # study_protocol_choices = SelectMultipleField(
    #         "Study/Project Protocol choices")#, choices=stu_protocols),
    #
    # acquisition_protocol_default = StringField(
    #         "Default project/study protocol",
    #         choices=[])#acq_protocols)
    # acquisition_protocol_choices = SelectMultipleField(
    #         "Sample Acquisition Protocol choices",
    #         choices=[], #acq_protocols,
    #         default=[])
    #
    # # sample_basetype_default = StringField("Default sample base type")
    # sample_basetype_choices = SelectMultipleField(
    #         "Sample base type choices", choices=SampleBaseType.choices()),

    sample_basetype_default = StringField(
            "Default sample base type",
            choices=SampleBaseType.choices(),
            default="FLU")
    #
    # sample_basetype_choices = SelectMultipleField(
    #         "Sample base type choices",
    #         choices=SampleBaseType.choices(),
    #         default=[]
    #         )
    #
    # sample_flu_type_default =  SelectField(
    #         "Default sample fluid type",
    #         choices=FluidSampleType.choices(),
    #         default='BLD')
    # sample_flu_type_choices = SelectMultipleField(
    #         "Sample fluid types",
    #         choices=FluidSampleType.choices(),
    #         default=[])
    #
    # container_basetype_default = SelectField(
    #         "Default Container Base Type",
    #         choices=ContainerBaseType.choices(),
    #         default = "LTS")
    # container_basetype_choices = SelectMultipleField(
    #         "Container Base Type choices",
    #         choices=ContainerBaseType.choices(),
    #         default=[])
    #
    # prm_container_default = SelectField(
    #         "Default primary container type",
    #         choices=FluidContainer.choices(),
    #         default = "CAT")
    # prm_containerprm_choices = SelectMultipleField(
    #         "Primary container type choices",
    #         choices=FluidContainer.choices(),
    #         default = [])
    #
    # lts_container_default = SelectField(
    #         "Default Long-term Preservation container",
    #         choices=CellContainer.choices(),
    #         default="D")
    #
    # lts_containerprm_choices = SelectMultipleField(
    #         "Long-term Preservation container choices",
    #         choices=CellContainer.choices(),
    #         default=[])

    # data_entry = {
    #         "site": {"default":1, "choices":[1,2]},
    #
    #         "consent_template": {"default": 2, "choices":[]},
    #         "protocol": {
    #             "STU": {"default": 19},
    #             "ACQ": {"default": 5},
    #         },
    #
    #         "sample_type": {
    #             "base_type": "FLU",
    #             "FLU": {"default": "BLD",
    #                     "choices": [],
    #                     },
    #             },
    #
    #         "container_type": {
    #             "base_type": {"default": "LTS"},
    #             "PRM": {
    #                 "container": {"default": "CAT"},
    #             },
    #             "LTS": {
    #                 "container": {"default": "D"},
    #             },
    #         },
    #     }