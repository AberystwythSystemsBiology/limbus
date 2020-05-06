from app import db

class SampleToCustomAttributeTextValue(db.Model):
    __tablename__ = "sample_to_custom_attribute_text_values"

    id = db.Column(db.Integer, primary_key=True)

    value = db.Column(db.String)
    custom_attribute_id = db.Column(db.Integer, db.ForeignKey("custom_attributes.id"))

    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now(), nullable=False)

class SampleToCustomAttributeNumericValue(db.Model):
    __tablename__ = "sample_to_custom_attribute_numeric_values"

    id = db.Column(db.Integer, primary_key=True)

    value = db.Column(db.String)
    custom_attribute_id = db.Column(db.Integer, db.ForeignKey("custom_attributes.id"))

    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now(), nullable=False)


class SampleToCustomAttributeOptionValue(db.Model):
    __tablename__ = "sample_to_custom_attribute_option_values"
    id = db.Column(db.Integer, primary_key=True)

    custom_option_id = db.Column(db.Integer, db.ForeignKey("custom_attribute_options.id"))

    custom_attribute_id = db.Column(db.Integer, db.ForeignKey("custom_attributes.id"))
    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"))

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)