from flask import redirect, abort, render_template, url_for, session, request, jsonify
from flask_login import current_user, login_required

from .models import *
from .. import db

from . import procedure
from .forms import DiagnosticProcedureCreationForm

import json

from .views import DiagnosticProceduresIndexView, DiagnosticProcedureView

@procedure.route("/")
@login_required
def index():
    procedures = DiagnosticProceduresIndexView()
    return render_template("procedure/index.html", procedures=procedures)

@procedure.route("/view/LIMBDIAG-<procedure_id>")
@login_required
def view(procedure_id):
    dpv = DiagnosticProcedureView(procedure_id)
    return render_template("procedure/view.html", dpv=dpv)

@procedure.route("/new", methods=["GET", "POST"])
def new():
    form = DiagnosticProcedureCreationForm()
    if form.validate_on_submit():
        dpc = DiagnosticProcedureClass(
            name = form.name.data,
            version = form.version.data,
            description = form.version.data,
            author_id = current_user.id,
        )

        db.session.add(dpc)
        db.session.flush()

        if form.from_file.data == True:
            data = json.load(form.json_file.data)
            for volume, data in data.items():
                dpv = DiagnosticProcedureVolume(
                    code = volume,
                    name = data["title"],
                    author_id = current_user.id,
                    class_id = dpc.id
                )

                db.session.add(dpv)
                db.session.flush()

                for sh_code, subheading in data["subheadings"].items():
                    dpsh = DiagnosticProcedureSubheading(
                        code = sh_code,
                        subheading = subheading["heading"],
                        author_id = current_user.id,
                        volume_id = dpv.id
                    )

                    db.session.add(dpsh)
                    db.session.flush()

                    for code, descr in subheading["codes"].items():
                        dp = DiagnosticProcedure(
                            code = code,
                            procedure = descr,
                            author_id = current_user.id,
                            subheading_id = dpsh.id
                        )

                        db.session.add(dp)

        
        db.session.commit()
        return redirect(url_for("procedures.index"))


    return render_template("procedure/new.html", form=form)