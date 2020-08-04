# Copyright (C) 2019  Keiron O'Shea <keo7@aber.ac.uk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from flask import redirect, abort, render_template, url_for, session, request, jsonify
from flask_login import current_user, login_required

from .. import processing

from ..forms import NewProtocolForm

from ... import db
from ...auth.models import User

from ..models import *
from ...document.models import Document
from ...document.routes import save_document
from ...document.models import DocumentType

from ..views import ProcessingProtocolsIndexView, ProcessingProtocolView


@processing.route("/protocols")
@login_required
def protocol_index():
    protocols = ProcessingProtocolsIndexView()
    return render_template("processing/protocols/index.html", protocols=protocols)


@processing.route("/protocols/new", methods=["GET", "POST"])
@login_required
def new_protocol():
    form = NewProtocolForm()
    if form.validate_on_submit():
        has_document = bool(form.document_upload.data)

        pt = ProcessingTemplate(
            name=form.name.data,
            type=form.protocol_type.data,
            sample_type=form.sample_type.data,
            has_document=has_document,
            author_id=current_user.id,
        )

        db.session.add(pt)
        db.session.flush()

        if has_document:
            doc_id = save_document(
                form.document_upload,
                "%s Document" % form.name.data,
                "",
                DocumentType.PROTO,
                current_user.id,
            )

            pttd = ProcessingTemplateToDocument(
                template_id=pt.id, document_id=doc_id, author_id=current_user.id
            )

            db.session.add(pttd)
            db.session.flush()

        db.session.commit()

        return redirect(url_for("processing.protocol_index"))
    return render_template("processing/protocols/new/one.html", form=form)


@processing.route("/protocols/view/LIMBPRO-<protocol_id>")
@login_required
def view_protocol(protocol_id):
    protocol = ProcessingProtocolView(protocol_id)

    return render_template("processing/protocols/view.html", protocol=protocol)
