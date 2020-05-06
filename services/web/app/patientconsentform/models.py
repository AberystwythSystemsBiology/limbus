from app import db

class ConsentFormTemplate(db.Model):
    __tablename__ = "consent_form_templates"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)

    version = db.Column(db.String(64))

    upload_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

    uploader = db.Column(db.Integer, db.ForeignKey("users.id"))


class ConsentFormTemplateQuestion(db.Model):
    __tablename__ = "consent_form_template_questions"

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String, nullable=False)

    template_id = db.Column(db.Integer, db.ForeignKey("consent_form_templates.id"))

    upload_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )
    uploader = db.Column(db.Integer, db.ForeignKey("users.id"))

