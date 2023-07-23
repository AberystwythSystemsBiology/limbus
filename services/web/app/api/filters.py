from ..auth.models import UserAccount


def _put():
    pass


def _get():
    pass


def _post():
    pass


def get_filters_and_joins(args: object, model: object) -> object:

    filters = {}
    joins = []

    for key, value in args.items():
        if type(value) == dict:
            joins.append(getattr(model, key).has(**value))
        elif type(value) == list:
            joins.append(getattr(model, key).in_(value))
        elif key in ['status'] and type(value) == str: # Dealing with multiple choice
            joins.append(getattr(model, key).in_(value.split(",")))
        else:
            filters[key] = value
    return filters, joins


def generate_base_query_filters(tokenuser: UserAccount, type: str):

    if tokenuser.account_type.value == "Administrator":
        return {}, True

    else:
        return {"is_locked": False}, True
