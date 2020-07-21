from flask import abort, current_app, request
from .auth.models import UserAccount, UserAccountToken
from flask_login import login_user, logout_user, current_user
from functools import wraps


def token_required(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        if request.method in ["OPTION"]:
            return f(*args, **kwargs)
        elif current_app.config.get('LOGIN_DISABLED'):
            return f(*args, **kwargs)
        elif "FlaskApp" in request.headers:
            if current_app.config.get("SECRET_KEY") == request.headers["FlaskApp"].replace('"', ''):
                print(current_user)
                return f(*args, **kwargs)
        elif "Email" in request.headers:
            email = request.headers["Email"].replace('"', '')
            token = request.headers["Token"].replace('"', '')
            user = UserAccount.query.filter_by(email=email).first()
            if user != None:
                user_token = UserAccountToken.query.filter_by(user_id=user.id).first()
                if user_token != None:
                    if user_token.verify_token(token):
                        return f(*args, **kwargs)
        return abort(401)
    return decorated_view


def as_kryten(f):
    """
    If you decorate a view with this, it will log you in to the bot
    account and allow you to enter biobank data. If Kryten is not
    present, it calls a 401. For example::

        @app.route("/setup")
        @as_kryten
        def setup_index():
            pass

    :param f: The view function to decorate.
    :return: function
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        kryten = UserAccount.query.filter_by(email="kryten@jupiterminingcorp.co.uk").first()
        if kryten is None:
            return abort(401)
        login_user(kryten)
        return f(*args, **kwargs)

    return decorated_function



def setup_mode(f):
    """
    If you decorate a view with this, it will check to see if a user account
    is present in the database before calling the actual view. If no user is
    present, it calls a 401. For example::

        @app.route("/setup")
        @check_if_user
        def setup_index():
            pass

    :param f: The view function to decorate
    :return: function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.email !=  "kryten@jupiterminingcorp.co.uk" or len(UserAccount.query.all()) > 1:
            return abort(401)
        return f(*args, **kwargs)

    return decorated_function