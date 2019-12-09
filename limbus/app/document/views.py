from flask import redirect, render_template, url_for, flash, g, current_app
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.utils import secure_filename

import random
import string

from . import document
from .models import Document, DocumentFile
from .forms import DocumentUploadForm

from .. import db

@login_required
@document.route("/")
def index():
    if current_user.is_admin:
        documents = Document.query.join(DocumentFile, Document.id == DocumentFile.document_id)
    else:
        documents = Document.query.filter(Document.uploader == current_user.id).all()
    return render_template("document/index.html", documents=documents)

@document.route("/upload", methods=["GET", "POST"])
def upload():
    form = DocumentUploadForm()
    if form.validate_on_submit():
        f = form.file.data

        folder_name = ''.join(random.choice(string.ascii_lowercase) for i in range(20))

        current_app.config["DOCUMENT_DIRECTORY"]


        document_file = DocumentFile(
            filename = secure_filename(f)
        )

        db.session.add(document_file)
        db.session.flush()

        document = Document(
            name = form.name.data,
            description = form.description.data,
            type = form.type.data,
            uploader = current_user.id,
            file_id = document_file.id
        )

        db.session.add(document)
        db.session.commit()

        return redirect(url_for("document.index"))


    return render_template("document/upload.html", form=form)