from .models import CustomAttributes
from ..auth.models import User
from .. import db
from ..ViewClass import ViewClass


class CustomAttributesIndexView(ViewClass):
    """
        This class returns an dictionary of information concerning attributes, as well as their author information.

        It is used in the following routes:
            - __init__.py :: index

        It is used in the following apis:
            - None.
    """
    def __init__(self):
        self.attributes = db.session.query(CustomAttributes, User).filter(CustomAttributes.author_id == User.id).all()

    def get_attributes(self) -> dict:
        data = {}
        for attribute, user in self.attributes:

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

