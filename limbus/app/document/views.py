from flask import redirect, render_template, url_for, flash, g
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.utils import secure_filename


from . import document
from .models import Document, DocumentFile
from .forms import DocumentUploadForm

from .. import db

@login_required
@document.route("/")
def index():
    if current_user.is_admin:
        documents = db.session.query(Document ,DocumentFile).filter(Document.file_id == DocumentFile.id).all()
    else:
        documents = Document.query.filter(Document.uploader == current_user.id).all()

    return render_template("document/index.html", documents=documents)

@document.route("/upload", methods=["GET", "POST"])
def upload():
    form = DocumentUploadForm()
    if form.validate_on_submit():
        f = form.file.data

        document_file = DocumentFile(
            filename = secure_filename(f)
        )

        db.session.add(document_file)
        db.session.flush()

        document = Document(
            name = form.name.data,
            description = form.description.data,
            type = form.description.data,
            uploader = current_user.id.data,
            file_id = document_file.id.data
        )

        db.session.add(document)
        db.session.commit()

        return redirect(url_for("document.index"))


    return render_template("document/upload.html", form=form)