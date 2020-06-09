from flask_wtf import FlaskForm
from wtforms import (
    FileField,
    StringField,
    SubmitField,
    DecimalField,
    BooleanField,
)
from wtforms.validators import DataRequired

class DiagnosticProcedureCreationForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    version = DecimalField("Version")
    description = StringField("Description")
    from_file = BooleanField("From File")
    json_file = FileField("Upload (*)")
    submit = SubmitField("Submit")