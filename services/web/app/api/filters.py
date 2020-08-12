from ..auth.models import UserAccount


def _put():
    pass


def _get():
    pass


def _post():
    pass


def generate_base_query_filters(tokenuser: UserAccount, type: str):

    if tokenuser.account_type.value is "Administrator":
        return {}, True

    else:
        return {"is_locked": False}, True
