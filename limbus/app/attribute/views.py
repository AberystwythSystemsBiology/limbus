from .models import CustomAttributes, CustomAttributeOption, CustomAttributeTextSetting, CustomAttributeNumericSetting
from ..auth.views import UserView
from .. import db

def CustomAttributesIndexView() -> dict:
    """
        This method returns an dictionary of information concerning attributes, as well as their author information.
    """
    attributes = db.session.query(CustomAttributes).all()

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


def CustomAttributeView(ca_id) -> dict:

    attribute = db.session.query(CustomAttributes).filter(CustomAttributes.id == ca_id).first_or_404()

    data = {
        "id" : attribute.id,
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

    if data["type"] == "Option":
        options = db.session.query(CustomAttributeOption).filter(CustomAttributeOption.custom_attribute_id == attribute.id).all()

        o_data = {}

        for option in options:
            o_data[option.id] = {
                "term": option.term,
                "accession": option.accession,
                "ref" : option.ref
            }

        data["option_info"] = o_data

    elif data["type"] == "Numeric":

        settings = db.session.query(CustomAttributeNumericSetting).filter(CustomAttributeNumericSetting.custom_attribute_id == attribute.id).first_or_404()

        data["numeric_settings"] = {
            "id" : settings.id,
            "measurement": settings.measurement,
            "prefix" : settings.prefix
        }

    else:

        settings = db.session.query(CustomAttributeTextSetting).filter(CustomAttributeTextSetting.custom_attribute_id == attribute.id).first_or_404()


        data["text_settings"] = {
            "id" : settings.id,
            "max_length": settings.max_length
        }



    return data