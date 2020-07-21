from flask import abort
from .auth.models import UserAccount
from flask_login import login_user, logout_user, current_user
from functools import wraps


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
        print(">>>>>>>>>>>>>>>>>>", UserAccount.query.all().count)
        if current_user.email !=  "kryten@jupiterminingcorp.co.uk" or len(UserAccount.query.all()) > 1:
            return abort(401)
        return f(*args, **kwargs)

    return decorated_function