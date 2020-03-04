from . import api

from .. import db
from flask import (
    redirect,
    render_template,
    url_for,
    abort,
    current_app,
    send_file,
    jsonify,
)
from flask_login import login_required, current_user
from datetime import datetime

from ..document.models import Document

@api.route("get_greeting")
def get_greeting():
    greetings = [
        ["Helo", "Welsh"],
        ["Hello", "English"],
        ["Ni Hao", "Mandarin"],
        ["Neih Ho", "Cantonese"],
        ["Szia", "Hungarian"],
        ["Moyo", "Tshiluba"],
        ["Zdravo", "Serbian"]
    ]

    return jsonify({"greeting"})

@api.route("document/<id>")
@login_required
def get_document(id):
    document = db.session.query(Document).filter(Document.id == id).first_or_404()

    response = {}
    for k, v in document.__dict__.items():
        if v == "":
            response[k] = None
        elif type(v) in [int, str]:
            response[k] = v
        elif type(v) == datetime:
            response[k] = v.strftime("%Y-%m-%d %H:%M:%S")
        try:
            response[k] = v.value
        except Exception:
            pass

    return jsonify(response), 201, {"Content-Type": "application/json"}
