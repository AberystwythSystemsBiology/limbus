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
    FieldList,
    SelectField,
    SelectMultipleField
)
from wtforms.validators import DataRequired, Email, EqualTo
from ...validators import validate_against_text

from ...auth.enums import Title, AccountType


from ...auth.models import UserAccount

from ...sample.enums import SampleBaseType, FluidSampleType, \
                    ContainerBaseType, FluidContainer, CellContainer

from flask import flash

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
    # print("data", data)
    if "account_type" in data:
        data["account_type"]= AccountType(data["account_type"]).name

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

        account_type = SelectField("Account Type",
               validators=[DataRequired()], choices=AccountType.choices())

        settings = FieldList(FormField(UserSettings), min_entries=1)

        submit = SubmitField("Update")

        def validate(self):
            for entry in self.settings.entries:
                print("access_level", entry.access_level.data)
                print("sites", entry.site_choices.data)

            # if not FlaskForm.validate(self):
            #     print("ok")
            #     return False

            if UserAccount.query.filter_by(email=self.email.data)\
                    .filter(UserAccount.id!=data["id"]).first():
                self.email.errors.append("Email address already in use.")
                flash("Email address already in use.")
                return False
                #raise ValidationError("Email address already in use.")

            return True

    return StaticForm(data=data)


class UserSettings(FlaskForm):
    class Meta:
        csrf = False

    access_choices = [(0, "None"), (1, "data_entry"), (2, "view_only")]
    access_level = SelectField("Access level", coerce=int,
                               choices=access_choices,
                               render_kw={"size": "1", "class": "form-control"}
                               )

    site_choices = SelectMultipleField("Work Sites",
                    choices=[],
                    render_kw={"size":"2", "class":"selectpicker"})
    # site_default = StringField("Default working site")

    # consent_template_default = SelectField("Default working consent template")
    # consent_template_choices = SelectMultipleField(
    #         "Consent template choices", choices=[])
    #
    # study_protocol_default = StringField("Default project/study protocol")#, choices=stu_protocols)
    # study_protocol_choices = SelectMultipleField(
    #         "Study/Project Protocol choices", choices=[])#, choices=stu_protocols),
    #
    # acquisition_protocol_default = StringField(
    #         "Default project/study protocol")
    #
    # acquisition_protocol_choices = SelectMultipleField(
    #         "Sample Acquisition Protocol choices",
    #         choices=[])
    #
    # # sample_basetype_default = StringField("Default sample base type")
    # sample_basetype_choices = SelectMultipleField(
    #         "Sample base type choices", choices=SampleBaseType.choices()),

    # sample_basetype_default = StringField(
    #         "Default sample base type",
    #         choices=SampleBaseType.choices(),
    #         default="FLU")
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
    #                 "container": {"default": "X"},
    #             },
    #         },
    #     }