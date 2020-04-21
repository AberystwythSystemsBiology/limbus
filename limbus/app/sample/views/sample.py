from ... import db

from ..models import *

from ...auth.models import User
from ...ViewClass import ViewClass

class SampleView(ViewClass):
    def __init__(self, sample_id):
        self.sample_id = sample_id

    def get_attributes(self) -> dict:
        sample, user = db.session.query(Sample, User)\
            .filter(Sample.id == self.sample_id)\
            .filter(Sample.author_id == User.id)\
            .first_or_404()

        data = {
            "biobank_barcode" : sample.biobank_barcode,
            "sample_type" : sample.sample_type.value,
            "sample_status" : sample.sample_status.value,
            "collection_date" : sample.collection_date,
            "quantity" : sample.quantity,
            "current_quantity": sample.current_quantity,
            "is_closed" : sample.is_closed,
            "disposal_instruction" : sample.disposal_instruction,
            "disposal_date" : sample.disposal_date,
            "create_date" : sample.creation_date,
            "update_date" : sample.update_date
        }

        data["custom_attributes"] = {

        }

        data["author_id"] = {
            "id" : user.id,
            "user" : user.name,
            "gravatar" : user.gravatar()
        }

        data["storage_info"] = {

        }

        data["consent_info"] = {

        }

        data["processing_info"] = {

        }

        return data