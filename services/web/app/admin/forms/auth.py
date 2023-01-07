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
    TextAreaField,
    SubmitField,
    ValidationError,
    SelectField,
    BooleanField,
    FormField,
    FieldList,
    SelectField,
    SelectMultipleField,
)
from wtforms.validators import DataRequired, Email, EqualTo, Length
from ...validators import validate_against_text

from ...auth.enums import Title, AccountType


from ...auth.models import UserAccount

from ...sample.enums import (
    SampleBaseType,
    FluidSampleType,
    CellSampleType,
    MolecularSampleType,
    ContainerBaseType,
    FluidContainer,
    CellContainer,
)

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


def AccountLockPasswordForm(email):
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



def AdminUserAccountEditForm(sites=[], data={}) -> FlaskForm:
    if "account_type" in data:
        data["account_type"] = AccountType(data["account_type"]).name

    class StaticForm(FlaskForm):
        title = SelectField(
            "Title", validators=[DataRequired()], choices=Title.choices()
        )

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

        account_type = SelectField(
            "Account Type", validators=[DataRequired()], choices=AccountType.choices()
        )

        use_template = SelectField(
            "Choose user setting from template",
            # coerce=int,
            choices=[],
            default=None,
            render_kw={"size": "1", "class": "form-control bd-light alert-info"},
        )

        set_to_template = SubmitField("Set",
                                      render_kw={"class": "btn btn-link float-right top10"})

        settings = FieldList(FormField(UserSettings), min_entries=1)
        submit = SubmitField("Update", render_kw={"class": "btn btn-success float-right top10"})

        def validate(self):
            if self.set_to_template.data and not self.set_to_template.data:
                return False

            if (
                UserAccount.query.filter_by(email=self.email.data)
                .filter(UserAccount.id != data["id"])
                .first()
            ):
                self.email.errors.append("Email address already in use.")
                flash("Email address already in use.")
                return False

            return True

    return StaticForm(data=data)


class UserSettings(FlaskForm):
    class Meta:
        csrf = False

    access_choices = [(1, "data_entry"), (2, "view_only")]
    access_level = SelectField(
        "Access level",
        coerce=int,
        choices=access_choices,
        render_kw={"size": "1", "class": "form-control bd-light"},
    )

    site_choices = SelectMultipleField(
        "Work Sites",
        choices=[], coerce=int,
        render_kw={"size": "1", "class": "selectpicker form-control wd=0.6"},
    )

    site_selected = TextAreaField(
        "Current",
        render_kw={"readonly": True, "rows": 5, "class": "form-control bd-light"},
    )
    # site_default = SelectField(
    #     "Default working site",
    #     choices=[], coerce=int,
    #     render_kw={"size": "1", "class": "form-control bd-light"},
    # )

    # -- Consent
    consent_template_choices = SelectMultipleField(
        "Consent template choices",
        choices=[], coerce=int,
        render_kw={"size": "1", "class": "selectpicker form-control wd=0.6"},
    )
    consent_template_selected = TextAreaField(
        "Current choice",
        render_kw = {"readonly": True, "rows": 5, "class": "form-control bd-light"},
    )
    consent_template_default = SelectField(
        "Default working consent template",
        choices=[], coerce=int,
        render_kw={"size": "1", "class": "form-control bd-light"},
    )

    # -- Study protocols
    study_protocol_choices = SelectMultipleField(
        "Study choices",
        choices=[], coerce=int,
        render_kw={"size": "1", "class": "selectpicker form-control wd=0.6"},
    )

    study_protocol_selected = TextAreaField(
        "Current choice",
        render_kw = {"readonly": True, "rows": 5, "class": "form-control bd-light"},
    )
    study_protocol_default = SelectField(
        "Default study",
        choices=[], coerce=int,
        render_kw={"size": "1", "class": "form-control bd-light"},
    )

    # -- sample acquisition protocols
    collection_protocol_choices = SelectMultipleField(
        "Sample acquisition protocol choices",
        choices=[], coerce=int,
        render_kw={"size": "1", "class": "selectpicker form-control wd=0.6"},
    )
    collection_protocol_selected = TextAreaField(
        "Current choice",
        render_kw = {"readonly": True, "rows": 5, "class": "form-control bd-light"},
    )
    collection_protocol_default = SelectField(
        "Default sample acquisition protocol",
        choices=[], coerce=int,
        render_kw={"size": "1", "class": "form-control bd-light"},
    )

    # -- sample processing protocols
    processing_protocol_choices = SelectMultipleField(
        "Sample processing protocol choices",
        choices=[], coerce=int,
        render_kw={"size": "1", "class": "selectpicker form-control wd=0.6"},
    )
    processing_protocol_selected = TextAreaField(
        "Current choice",
        render_kw = {"readonly": True, "rows": 5, "class": "form-control bd-light"},
    )
    processing_protocol_default = SelectField(
        "Default sample processing protocol",
        choices=[], coerce=int,
        render_kw={"size": "1", "class": "form-control bd-light"},
    )

    sample_basetype_default = SelectField(
            "Default sample base type",
            choices=SampleBaseType.choices(),
            default="FLU",
            render_kw={"size": "1", "class": "form-control bd-light"},
    )
    #
    # sample_basetype_choices = SelectMultipleField(
    #         "Sample base type choices",
    #         choices=SampleBaseType.choices(),
    #         default=[]
    #         )
    #
    sample_flu_type_default =  SelectField(
            "Default sample fluid type",
            choices=FluidSampleType.choices(),
            default='BLD', render_kw={"size": "1", "class": "form-control bd-light"}
    )

    # sample_flu_type_choices = SelectMultipleField(
    #         "Sample fluid types",
    #         choices=FluidSampleType.choices(),
    #         default=[])

    sample_cel_type_default =  SelectField(
            "Default solid sample type",
            choices=CellSampleType.choices(),
            default='BLD', render_kw={"size": "1", "class": "form-control bd-light"}
    )

    sample_mol_type_default =  SelectField(
            "Default molecular sample type",
            choices=MolecularSampleType.choices(),
            default=None, render_kw={"size": "1", "class": "form-control bd-light"}
    )

    container_basetype_default = SelectField(
            "Default Container Base Type",
            choices=ContainerBaseType.choices(),
            default = "LTS", render_kw={"size": "1", "class": "form-control bd-light"}
    )

    # container_basetype_choices = SelectMultipleField(
    #         "Container Base Type choices",
    #         choices=ContainerBaseType.choices(),
    #         default=[])
    #
    prm_container_default = SelectField(
            "Default primary container type",
            choices=FluidContainer.choices(),
            default = "CAT", render_kw={"size": "1", "class": "form-control bd-light"}
    )

    # prm_container_choices = SelectMultipleField(
    #         "Primary container type choices",
    #         choices=FluidContainer.choices(),
    #         default = [])
    #

    lts_container_default = SelectField(
            "Default Long-term Preservation container",
            choices=CellContainer.choices(),
            default="D", render_kw={"size": "1", "class": "form-control bd-light"}
    )

    # lts_containerprm_choices = SelectMultipleField(
    #         "Long-term Preservation container choices",
    #         choices=CellContainer.choices(),
    #         default=[])

    saveto_template_name = StringField(
        "To save setting as template, provide a  nick name here",
        default=None,
        validators=[Length(min=4, max=36)],
        render_kw={"size":"1", "class": "form-control bd-light alert-info"}
    )

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
