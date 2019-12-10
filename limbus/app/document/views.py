from flask import redirect, render_template, url_for, flash, g, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

import random
import string
import os

from . import document
from .models import Document, DocumentFile
from .forms import DocumentUploadForm

from .. import db

@login_required
@document.route("/")
def index():
    if current_user.is_admin:
        documents = Document.query.join(DocumentFile, DocumentFile.document_id == Document.id).all()
    else:
        documents = Document.query.filter(Document.uploader == current_user.id).all()

    return render_template("document/index.html", documents=documents)

@document.route("/upload", methods=["GET", "POST"])
def upload():
    form = DocumentUploadForm()
    if form.validate_on_submit():
        f = form.file.data

        folder_name = ''.join(random.choice(string.ascii_lowercase) for _ in range(20))

        document_dir = current_app.config["DOCUMENT_DIRECTORY"]

        rel_path = os.path.join(document_dir, folder_name)
        os.makedirs(rel_path)

        sfn = secure_filename(f)

        filepath = os.path.join(rel_path, sfn)

        document = Document(
            name = form.name.data,
            description = form.description.data,
            type = form.type.data,
            uploader = current_user.id,
        )

        db.session.add(document)
        db.session.commit()

        db.session.flush()


        document_file = DocumentFile(
            filename = sfn,
            filepath = filepath,
            uploader=current_user.id,
            document_id=document.id
        )

        db.session.add(document_file)
        db.session.commit()

        return redirect(url_for("document.index"))


    return render_template("document/upload.html", form=form)

@document.route("/view/DOC<doc_id>")
def view(doc_id):
    document = Document.query.filter(Document.id == doc_id).first()

    files = DocumentFile.query.filter(DocumentFile.document_id == doc_id).all()

    return render_template("document/view.html", document=document, files=files)

@document.route("/download/FILE<file_id>")
def get_file(file_id):
    file = DocumentFile.query.filter(DocumentFile.id == file_id).first()
    return send_file(file.filepath)