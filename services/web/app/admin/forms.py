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

from ..auth.enums import Title


from ..auth.models import UserAccount


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
