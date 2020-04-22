from flask import (
    redirect,
    render_template,
    url_for,
    abort,
    current_app,
    send_file,
    session,
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from ..misc.generators import generate_random_hash

import random
import string
import os

from . import document
from .models import Document, DocumentFile, PatientConsentForm, DocumentType
from .forms import (
    DocumentUploadForm,
    PatientConsentFormInformationForm,
    DocumentUploadFileForm,
)

from ..sample.models import SampleDocumentAssociation

from ..auth.models import User

from .. import db


@login_required
@document.route("/")
def index():
    if current_user.is_admin:

        documents = (
            db.session.query(User, Document).filter(Document.uploader == User.id).all()
        )

    else:
        documents = Document.query.filter(Document.uploader == current_user.id).all()

    return render_template("document/index.html", documents=documents)


@document.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    form = DocumentUploadForm()
    if form.validate_on_submit():
        hash = generate_random_hash()

        session["%s document_info" % (hash)] = {
            "name": form.name.data,
            "description": form.description.data,
            "type": form.type.data,
        }

        return redirect(url_for("document.document_upload", hash=hash))

    return render_template("document/upload/index.html", form=form)


def save_document(file, name, description, type, uploader, commit=False) -> int:
    filename = file.data.filename
    folder_name = "".join(random.choice(string.ascii_lowercase) for _ in range(20))
    document_dir = current_app.config["DOCUMENT_DIRECTORY"]
    rel_path = os.path.join(document_dir, folder_name)
    os.makedirs(rel_path)
    sfn = secure_filename(filename)
    filepath = os.path.join(rel_path, sfn)

    document = Document(
        name=name,
        description=description,
        type=type,
        uploader=uploader,
    )

    db.session.add(document)
    db.session.flush()

    document_file = DocumentFile(
        filename=sfn,
        filepath=filepath,
        uploader=current_user.id,
        document_id=document.id,
    )

    file.data.save(filepath)
    db.session.add(document_file)

    if commit:
        db.session.commit()

    return document.id


@document.route("/upload/file/<hash>", methods=["GET", "POST"])
@login_required
def document_upload(hash):
    form = DocumentUploadFileForm()

    if form.validate_on_submit():
        document_info = session["%s document_info" % (hash)]
        document_id = save_document(form.file, document_info["name"], document_info["description"], document_info["type"], current_user.id)

        if "%s patient_consent_info" % (hash) in session:
            consent_info = session["%s patient_consent_info" % (hash)]

            pcf = PatientConsentForm(
                academic=consent_info["academic"],
                commercial=consent_info["commercial"],
                animal=consent_info["animal"],
                genetic=consent_info["genetic"],
                indefinite=True,
                document_id=document_id
            )

            db.session.add(pcf)

        db.session.commit()

        return redirect(url_for("document.index"))

    return render_template("document/upload/upload.html", form=form, hash=hash)


@document.route("/view/LIMBDOC-<doc_id>")
@login_required
def view(doc_id):

    upload_user, document = (
        db.session.query(User, Document)
        .filter(Document.id == doc_id)
        .filter(DocumentFile.uploader == User.id)
        .first()
    )

    if current_user.is_admin or upload_user.id == current_user.id:

        files = (
            db.session.query(User, DocumentFile)
            .filter(DocumentFile.uploader == User.id)
            .filter(DocumentFile.document_id == doc_id)
            .all()
        )

        # TODO: Build an association view class
        associated_document = (
            db.session.query(SampleDocumentAssociation)
            .filter(SampleDocumentAssociation.document_id == doc_id)
            .all()
        )

        return render_template(
            "document/view.html",
            document=document,
            upload_user=upload_user,
            files=files,
            associated_document=associated_document,
        )

    else:
        return abort(401)


@document.route("/download/D<doc_id>F<file_id>")
@login_required
def get_file(doc_id, file_id):
    file = DocumentFile.query.filter(DocumentFile.id == file_id).first()
    if current_user.is_admin or file.uploader == current_user.id:
        return send_file(file.filepath)
    else:
        return abort(401)
