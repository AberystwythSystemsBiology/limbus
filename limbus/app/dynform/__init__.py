# This is where all of the dynamic form generation stuff can be found.

from ..sample.enums import SampleAttributeTypes
from ..sample.models import SampleAttributeOption
from wtforms import SelectField, StringField, SubmitField, DateField, BooleanField, TextAreaField, TextField

from .. import db

import inflect
p = inflect.engine()

class DynamicAttributeFormGenerator():
    def __init__(self, query, form):
        self._query = query
        self._form = form

    def _iterate_query(self):
        for attr in self._query:
            if attr.type == SampleAttributeTypes.TEXT:
                setattr(self._form, p.number_to_words(attr.id), TextAreaField(attr.term))
            elif attr.type == SampleAttributeTypes.OPTION:
                options = db.session.query(SampleAttributeOption).filter(SampleAttributeOption.sample_attribute_id == attr.id).all()
                setattr(self._form, p.number_to_words(attr.id), SelectField(attr.term, choices=[(x.term, x.id) for x in options]))


    def _inject_submit(self):
        setattr(self._form, "submit", SubmitField())

    def make_form(self):
        self._iterate_query()
        self._inject_submit()
        return self._form()

class DynamicSelectFormGenerator():
    def __init(self, query, form):
        pass

    def _inject_submit(self):
        setattr(self._form, "submit", SubmitField())