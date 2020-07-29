from flask_wtf import FlaskForm
from wtforms import (
    PasswordField,
    StringField,
    SubmitField,
    ValidationError,
    SelectField,
)
from wtforms.validators import DataRequired, Email, EqualTo

from .models import UserAccount

from .enums import Title

class LoginForm(FlaskForm):
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


class PasswordChangeForm(FlaskForm):
    current_password = PasswordField(
        "Current Password",
        description="For security reasons, please enter your current password",
        validators=[
            DataRequired()
        ]
    )
    password = PasswordField(
        "Password",
        description="Please ensure that you provide a secure password",
        validators=[
            DataRequired(),
            EqualTo("confirm_password", message="Passwords must match"),
        ],
    )
    confirm_password = PasswordField("Confirm Password")

    submit = SubmitField("Register")


class UserAccountEditForm(FlaskForm):
    title = SelectField("Title", validators=[DataRequired()], choices=Title.choices())

    first_name = StringField("First Name", validators=[DataRequired()])
    middle_name = StringField("Middle Name")
    last_name = StringField("Last Name", validators=[DataRequired()])
    submit = SubmitField("Register")

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
    confirm_password = PasswordField("Confirm Password")

    submit = SubmitField("Register")

    def validate_email(self, field):
        if UserAccount.query.filter_by(email=field.data).first():
            raise ValidationError("Email address already in use.")
