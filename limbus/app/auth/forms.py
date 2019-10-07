from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, ValidationError, SelectField
from wtforms.validators import DataRequired, Email, EqualTo

from .models import User
from ..misc.models import ContactInformation, TitleType

class LoginForm(FlaskForm):
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")

class RegistrationForm(FlaskForm):

    email = StringField("Email Address", description="We'll never share your email with anyone else.", validators=[DataRequired(), Email()])

    title = SelectField("Title", validators=[DataRequired()], choices=[(x.name, x.value) for x in TitleType])

    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])

    phone_number = StringField("Phone Number")

    street_address_one = StringField("Street Address 1", description="Street and number, P.O. box, c/o.")
    street_address_two = StringField("Street Address 2", description="Flat, suite, unit, building, floor, etc.")
    city = StringField("Town/City")
    county = StringField("County")
    country = SelectField("Country", choices=[("gb", "United Kingdom")])

    password = PasswordField("Password", description="Please ensure that you provide a secure password", validators=[DataRequired(), EqualTo("confirm_password", message="Passwords must match")])
    confirm_password = PasswordField("Confirm Password")

    submit = SubmitField("Register")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email address already in use.")