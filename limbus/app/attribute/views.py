from .models import CustomAttributes
from .enums import CustomAttributeTypes
from ..auth.views import UserView
from .. import db

def CustomAttributesIndexView() -> dict:
    """
        This method returns an dictionary of information concerning attributes, as well as their author information.
    """
    attributes = db.session.query(CustomAttributes).all()

    data = {}

    for attribute in attributes:

        data[attribute.id] = {
            "term" : attribute.term,
            "description" : attribute.description,
            "type" : attribute.type.value,
            "accession": attribute.accession,
            "ref": attribute.ref,
            "element": attribute.element.value,
            "required": attribute.required,
            "creation_date": attribute.creation_date,
            "user_information" : UserView(attribute.author_id)
        }

        return data


def CustomAttributeView(ca_id) -> dict:

    attribute = db.session.query(CustomAttributes).filter(CustomAttributes.id == ca_id).first_or_404()

    data = {
        "id" : attribute.id,
        "term" : attribute.term,
        "description" : attribute.description,
        "type" : attribute.type.value,
        "accession": attribute.accession,
        "ref": attribute.ref,
        "element": attribute.element.value,
        "required": attribute.required,
        "creation_date": attribute.creation_date,
        "user_information" : UserView(attribute.author_id)
    }

    if data["type"] == "Option":
        options = db.session.query()

        pass

    return data