from .models import CustomAttributes
from ..auth.models import User
from .. import db

def CustomAttributesIndexView():
    """
        This method returns an dictionary of information concerning attributes, as well as their author information.
    """
    attributes = db.session.query(CustomAttributes, User).filter(CustomAttributes.author_id == User.id).all()

    data = {}

    for attribute, user in attributes:

        data[attribute.id] = {
            "term" : attribute.term,
            "description" : attribute.description,
            "type" : attribute.type.value,
            "accession": attribute.accession,
            "ref": attribute.ref,
            "element": attribute.element.value,
            "required": attribute.required,
            "creation_date": attribute.creation_date,
            "user_information" : {
                "email": user.email,
                "name": user.name,
                "gravatar": user.gravatar()
            }
        }

        return data

