from flask import abort
from .auth.models import UserAccount
from functools import wraps


def check_if_user(f):
    """
    If you decorate a view with this, it will check to see if a user account
    is present in the database before calliing the actual view. If no user is
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
        if UserAccount.query.first():
            return abort(401)
        return f(*args, **kwargs)

    return decorated_function