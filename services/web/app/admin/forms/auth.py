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
)
from wtforms.validators import DataRequired, Email, EqualTo
from ...validators import validate_against_text

from ...auth.enums import Title


from ...auth.models import UserAccount


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
