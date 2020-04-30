from .models import CustomAttributes
from ..auth.views import UserView
from .. import db

def CustomAttributesIndexView() -> dict:
    """
        This method returns an dictionary of information concerning attributes, as well as their author information.
    """
    attributes = db.session.query(CustomAttributes).filter().all()

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

