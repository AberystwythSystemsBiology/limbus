from ... import db
from ..models import SampleAttribute
from ...auth.models import User
from ...ViewClass import ViewClass

class SampleAttributesIndexView(ViewClass):

    def get_attributes(self) -> dict:
        attributes = (
            db.session.query(SampleAttribute, User)
                .filter(SampleAttribute.author_id == User.id)
                .all()
        )

        data = {}

        for attr, user in attributes:
            data[attr.id] = {
                "term" : attr.term,
                "type" : attr.type,
                "creation_date" : attr.creation_date,
                "required" : attr.required,
                "author_id" : {
                    "id": user.id,
                    "name": user.name,
                    "gravatar": user.gravatar()
                }
            }

        return data

class SampleAttributeView(ViewClass):
    def __init__(self, attribute_id):
        self.attribute = attribute_id

    def get_attributes(self) -> dict:

        attribute, user = (
            db.session.query(SampleAttribute, User)
                .filter(SampleAttribute.author_id == User.id)
                .first_or_404()
        )

        data = {
            "id" : attribute.id,
            "term" : attribute.term,
            "creation_date": attribute.creation_date,
            "type": attribute.type,
            "author_id" : {
                "id": user.id,
                "name": user.name,
                "gravatar": user.gravatar()
            }
        }


        return data


