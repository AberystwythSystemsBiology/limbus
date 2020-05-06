from ..FormEnum import FormEnum


class CustomAttributeTypes(FormEnum):
    TEXT = "Text"
    NUMERIC = "Numeric"
    OPTION = "Option"


class CustomAttributeElementTypes(FormEnum):
    ALL = "All"
    SAMPLE = "Sample"
    PROTOCOL = "Protocol"
    TRANSFER = "Transfer"
    DONOR = "Donor"
    STORAGE = "Storage"
