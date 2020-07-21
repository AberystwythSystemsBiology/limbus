from . import auth
from .. import db
from flask import request
from flask_login import login_required

from .views import basic_user_accounts_schema
from .models import UserAccount

@auth.route("/api")
def api_home():
    return {"results": basic_user_accounts_schema.dump(UserAccount.query.all())}

@auth.route("/api/user/new", methods=["POST"])
@login_required
def new_user():

    json_data = request.get_json()

    if not json_data:
        return {"message": "No input data provided"}, 400

    user_account = UserAccount(**json_data)
    db.session.add(user_account)
    db.session.commit()
    db.session.flush()

    return {"success": True, "id":  user_account.id}, 200