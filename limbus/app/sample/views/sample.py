from ... import db

from ..models import *

from ...auth.models import User
from ...ViewClass import ViewClass

from ...document.models import Document
from ...processing.models import ProcessingTemplate

class SampleView(ViewClass):
    def __init__(self, sample_id):
        self.sample_id = sample_id

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
        return {}

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
        self._sample, self._user = db.session.query(Sample, User)\
            .filter(Sample.id == self.sample_id)\
            .filter(Sample.author_id == User.id)\
            .first_or_404()



        data = {
            "id" : self._sample.id,
            "biobank_barcode" : self._sample.biobank_barcode,
            "sample_type" : self._sample.sample_type,
            "sample_status" : self._sample.sample_status,
            "collection_date" : self._sample.collection_date,
            "quantity" : self._sample.quantity,
            "current_quantity": self._sample.current_quantity,
            "is_closed" : self._sample.is_closed,
            "disposal_instruction" : self._sample.disposal_instruction,
            "disposal_date" : self._sample.disposal_date,
            "create_date" : self._sample.creation_date,
            "update_date" : self._sample.update_date
        }


        data["author_id"] = {
            "id" : self._user.id,
            "user" : self._user.name,
            "gravatar" : self._user.gravatar()
        }

        data["custom_attributes"] = self._get_custom_attrs()

        data["storage_info"] = self._get_storage()

        data["consent_info"] = self._get_consent_info()

        data["processing_info"] = self._get_processing_info()

        return data