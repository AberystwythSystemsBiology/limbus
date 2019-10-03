from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo

from .models import User

class LoginForm(FlaskForm):
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")

class RegistrationForm(FlaskForm):
    email = StringField("Email Address", description="We'll never share your email with anyone else.", validators=[DataRequired(), Email()])

    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])

    password = PasswordField("Password", validators=[DataRequired(), EqualTo("confirm_password", message="Passwords must match")])
    confirm_password = PasswordField("Confirm Password")

    submit = SubmitField("Register")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email address already in use.")