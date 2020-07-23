from . import auth
from .. import db
from flask import request
from flask_login import login_required, current_user

from ..decorators import token_required

from .views import basic_user_accounts_schema, full_user_account_schema
from .models import UserAccount

@auth.route("/api")
@token_required
def api_home():
    return {"results": basic_user_accounts_schema.dump(UserAccount.query.all())}

@auth.route("/api/user/<id>", methods=["GET"])

def api_view_user(id: int):
    # TODO: Check if admin or if the current user id == id.
    return full_user_account_schema.dump(UserAccount.query.filter_by(id=id).first())

#
# class Projects(db.Model):
#     id = db.Col(Int)
#     name = db.Col(Str)
#     uids = db.relationship("UserToProject", many=True)
#
# class UserToProject(db.Model):
#     id = db.Col(Int)
#     user_id = db.Col(Int, db.FK("users.id")
#     project_id = db.Col(Int, db.FK("project.id")
#

# class UserAccounts....
# ...........
#        id =
#        projects = db.relationship("Projects", many=True)

# user.projects = [<Project 1>, <Project 2> , 3, 4]

# @sample.route("/api/<id>/<project_id>")
# @check_if_admin
# def api_view_sample(project_id, id):
#     sample = Sample.query.filter_by(id = id).first()
#     ret = False
#     if project:
#         # Validate project integrity
#         # if Projects.query.filter_by(current_user.id in uids, project_id = sample.project_id).first() != None:
#               ret = True
#     if ret == True:
#          return full_sample_schema.dump(sample)
#     else:
#          abort(401)
#
@auth.route("/api/user/new", methods=["POST"])
def api_new_user():

    json_data = request.get_json()

    if not json_data:
        return {"message": "No input data provided"}, 400

    user_account = UserAccount(**json_data)
    db.session.add(user_account)
    db.session.commit()
    db.session.flush()

    return {"success": True, "id":  user_account.id}, 200