from flask import redirect, render_template, url_for, flash, g
from flask_login import login_required, login_user, logout_user, current_user

from . import document
from .models import Document, DocumentFile
from .forms import DocumentUploadForm

from .. import db

@login_required
@document.route("/")
def index():
    print(dir(current_user))
    if current_user.is_admin:
        documents = db.session.query(Document ,DocumentFile).filter(Document.file_id == DocumentFile.id).all()
    else:
        documents = Document.query.filter(Document.uploader == current_user.id).all()
    return render_template("document/index.html", documents=documents)

@document.route("/upload")
def upload():
    form = DocumentUploadForm()
    return render_template("document/upload.html", form=form)