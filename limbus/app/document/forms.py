from flask_wtf import FlaskForm
from wtforms import FileField, StringField, SubmitField, ValidationError, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, URL

from .models import DocumentType

class DocumentUploadForm(FlaskForm):
    name = StringField("Document Name", validators=[DataRequired()], description="Textual string of letters denoting the name of the document in English")
    type = SelectField("Document Type", validators=[DataRequired()], choices=[(x.name, x.value) for x in DocumentType])
    description = StringField("Document Description")
    file = FileField(validators=[DataRequired()])

    submit = SubmitField("Upload")

