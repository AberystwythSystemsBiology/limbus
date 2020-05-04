from ... import db

from ..models import *

from ...auth.views import UserView

from ...document.models import Document
from ...processing.models import ProcessingTemplate

from ...patientconsentform.models import *

def BasicSampleView(sample_id: int):
    sample = db.session.query(Sample).filter(Sample.id == sample_id).first_or_404()

    return {
        "id": sample.id,
        "uuid": sample.uuid,
        "biobank_barcode": sample.biobank_barcode,
        "collection_date": sample.collection_date,
        "sample_status": sample.sample_status,
        "disposal_instruction": sample.disposal_instruction,
        "disposal_date": sample.disposal_date,
        "creation_date": sample.creation_date,
        "update_date": sample.update_date,
        "author_information": UserView(sample.author_id)
    }

def SampleView(sample_id: int) -> dict:

    def _get_consent_information() -> dict:
        pass

    def _get_processing_information() -> dict:
        pass

    def _get_custom_attributes() -> dict:
        pass

    def _get_sample_to_type(sample_type) -> dict:
        print(">>>>>>>> test", type(sample_type))

        if sample_type == "Fluid":
            print(">>>>>>>> test", sample_type)
    
    sample = db.session.query(Sample).filter(Sample.id == sample_id).first_or_404()

    data = {
        "id": sample.id,
        "uuid": sample.uuid,
        "biobank_barcode": sample.biobank_barcode,
        "collection_date": sample.collection_date,
        "sample_status": sample.sample_status,
        "disposal_instruction": sample.disposal_instruction,
        "disposal_date": sample.disposal_date,
        "creation_date": sample.creation_date,
        "update_date": sample.update_date,
        "current_quantity": sample.current_quantity,
        "quantity": sample.quantity,
        "author_information": UserView(sample.author_id),

    }

    _get_sample_to_type(sample.sample_type)


    return data