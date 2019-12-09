from flask_wtf import FlaskForm
from wtforms import FileField, StringField, SubmitField, ValidationError, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, URL

class DocumentUploadForm(FlaskForm):
    name = StringField("Document Name", validators=[DataRequired()], description="Textual string of letters denoting the name of the document in English")
    description = StringField("Document Description")
    file = FileField()
    submit = SubmitField("Upload")

