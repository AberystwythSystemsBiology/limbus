from .enums import CustomAttributeTypes, CustomAttributeElementTypes
from app import db


class CustomAttributes(db.Model):
    __tablename__ = "custom_attributes"

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(1024))

    term = db.Column(db.String(128))
    accession = db.Column(db.String(64))
    ref = db.Column(db.String(64))

    element = db.Column(db.Enum(CustomAttributeElementTypes))

    required = db.Column(db.Boolean(), default=False)

    type = db.Column(db.Enum(CustomAttributeTypes))

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )


class CustomAttributeTextSetting(db.Model):
    __tablename__ = "custom_attribute_text_settings"

    id = db.Column(db.Integer, primary_key=True)
    max_length = db.Column(db.Integer, nullable=False)

    custom_attribute_id = db.Column(db.Integer, db.ForeignKey("custom_attributes.id"))

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )


class CustomAttributeNumericSetting(db.Model):
    __tablename__ = "custom_attribute_numeric_settings"

    id = db.Column(db.Integer, primary_key=True)

    custom_attribute_id = db.Column(db.Integer, db.ForeignKey("custom_attributes.id"))

    measurement = db.Column(db.String(32))
    prefix = db.Column(db.String(32))

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )


class CustomAttributeOption(db.Model):
    __tablename__ = "custom_attribute_options"

    id = db.Column(db.Integer, primary_key=True)

    term = db.Column(db.String(128))
    accession = db.Column(db.String(64))
    ref = db.Column(db.String(64))

    custom_attribute_id = db.Column(db.Integer, db.ForeignKey("custom_attributes.id"))

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )
