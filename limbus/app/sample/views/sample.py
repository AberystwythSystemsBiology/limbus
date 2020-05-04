from ... import db

from ..models import *

from ...auth.models import User
from ...ViewClass import ViewClass

from ...document.models import Document
from ...processing.models import ProcessingTemplate

from ...patientconsentform.models import *

class SampleView(ViewClass):
    def __init__(self, sample_id):
        self.sample_id = sample_id
        self.db_sessions = {

        }

    def _get_custom_attrs(self):
        # TODO: Fix this.
        option_attrs = (
            db.session.query(
                SampleAttribute, SampleAttributeOptionValue, SampleAttributeOption
            )
                .filter(SampleAttributeOptionValue.sample_id == self.sample_id)
                .filter(SampleAttributeOptionValue.sample_attribute_id == SampleAttribute.id)
                .filter(SampleAttributeOptionValue.sample_option_id == SampleAttributeOption.id)
                .all()
        )

        return {}

    def _get_storage(self):
        return {}

    def _get_processing_info(self):
        _, template = (
            db.session.query(SampleProcessingTemplateAssociation, ProcessingTemplate)
                .filter(SampleProcessingTemplateAssociation.sample_id == self.sample_id)
                .filter(
                ProcessingTemplate.id == SampleProcessingTemplateAssociation.template_id
            )
                .first_or_404()
        )

        return {
            "id": template.id,
            "name": template.name,
            "type": template.type,
            "sample_type": template.sample_type,
            "upload_type": template.upload_type
        }


    def _get_consent_info(self):
        spcta, cft =  db.session.query(
            SamplePatientConsentFormTemplateAssociation, ConsentFormTemplate
        ).filter(SamplePatientConsentFormTemplateAssociation.sample_id == self.sample_id).filter(
            ConsentFormTemplate.id == SamplePatientConsentFormTemplateAssociation.template_id
        ).first_or_404()

        return {
            "id": cft.id,
            "association_id": spcta.id
        }

    def _get_documents(self):
        associated_document, documents = (
            db.session.query(SampleDocumentAssociation, Document)
                .filter(SampleDocumentAssociation.sample_id == self.sample_id)
                .filter(SampleDocumentAssociation.document_id == Document.id)
                .all()
        )

        docs = {}

        for document in documents:
            docs[document.id] = {
                "name": document.name,
                "description": document.description,
                "type": document.type,
                "upload_date": document.upload_date,
            }

        return docs

    def get_attributes(self) -> dict:
        sample, user = db.session.query(Sample, User)\
            .filter(Sample.id == self.sample_id)\
            .filter(Sample.author_id == User.id)\
            .first_or_404()



        data = {
            "id" : sample.id,
            "uuid": sample.uuid,
            "biobank_barcode" : sample.biobank_barcode,
            "sample_type" : sample.sample_type,
            "sample_status" : sample.sample_status,
            "collection_date" : sample.collection_date,
            "quantity" : sample.quantity,
            "current_quantity": sample.current_quantity,
            "is_closed" : sample.is_closed,
            "disposal_instruction" : sample.disposal_instruction,
            "disposal_date" : sample.disposal_date,
            "create_date" : sample.creation_date,
            "update_date" : sample.update_date
        }


        data["author_id"] = {
            "id" : user.id,
            "user" : user.name,
            "gravatar" : user.gravatar()
        }

        self.db_sessions["sample"] = sample
        self.db_sessions["user"] = user


        data["storage_info"] = self._get_storage()

        data["consent_info"] = self._get_consent_info()

        data["processing_info"] = self._get_processing_info()

        return data