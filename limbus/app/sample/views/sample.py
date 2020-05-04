from ... import db

from ..models import *

from ...auth.views import UserView

from ...attribute.models import *
from ...document.models import Document
from ...processing.models import ProcessingTemplate

from ...patientconsentform.models import *

from ..enums import SampleType

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

    def _get_custom_attributes(sample_id: int) -> dict:
        text_values = db.session.query(CustomAttributes, SampleToCustomAttributeTextValue).filter(SampleToCustomAttributeTextValue.sample_id == sample_id).filter(SampleToCustomAttributeTextValue.custom_attribute_id == CustomAttributes.id).all()

        #numeric_values = db.session.query(CustomAttributes, SampleToCustomAttributeNumericValue).filter(SampleToCustomAttributeNumericValue.sample_id == sample_id).filter(SampleToCustomAttributeNumericValue.custom_attribute_id == CustomAttributes.id).all()
        

        custom_values = {}

        for attribute, value in text_values:
            custom_values[attribute.term] = value.value
        
        '''
        for attribute, value in numeric_values:
            custom_values[attribute.term] = value.value
        '''

        return custom_values

    def _get_sample_to_type(sample_type, id) -> dict:
        if sample_type == SampleType.CEL:
            sample_to_type = db.session.query(SampleToCellSampleType).filter(SampleToCellSampleType.sample_id == id).first_or_404()
        
        return {
            "sample_type": sample_type,
            "storage_type": sample_to_type.sample_type
        }

    
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

    data["sample_type_info"] = _get_sample_to_type(sample.sample_type, sample.id)
    data["custom_attribute_data"] = _get_custom_attributes(sample.id)



    return data