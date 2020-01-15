from flask import Blueprint, render_template
from flask_login import current_user

misc = Blueprint("misc", __name__)

from ..document.models import Document, DocumentFile
from ..sample.models import Sample, SampleAttribute

from .. import db

@misc.route("/")
def index():
    if current_user.is_authenticated:

        # Just because migrate isn't working
        # db.drop_all()

        document_count = db.session.query(Document).count()
        document_file_count = db.session.query(DocumentFile).count()

        sample_count = db.session.query(Sample).count()
        sample_attribute_count = db.session.query(SampleAttribute).count()

        return render_template("misc/panel.html",
                               document_count=document_count,
                               document_file_count=document_file_count,
                               sample_count=sample_count,
                               sample_attribute_count=sample_attribute_count
                               )
    else:
        return render_template("misc/index.html")

@misc.route("/license")
def license():
    return render_template("misc/license.html")

@misc.route("/team")
def team():
    return render_template("misc/team.html")