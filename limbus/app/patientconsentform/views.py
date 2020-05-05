from .. import db
from .models import ConsentFormTemplate, ConsentFormTemplateQuestion

from ..auth.views import UserView

def PatientConsentFormIndexView() -> dict:
    data = {}

    for template in db.session.query(ConsentFormTemplate).all():
        data[template.id] = {
            "name": template.name,
            "version": template.version,
            "upload_date": template.upload_date,
            "update_date": template.update_date,
            "user_information": UserView(template.uploader)
        }

    return data

def PatientConsentFormView(id) -> dict:

    cft = db.session.query(ConsentFormTemplate).filter(ConsentFormTemplate.id == id).first_or_404()

    data = {
        "id": id,
        "name" : cft.name,
        "version" : cft.version,
        "upload_date" : cft.upload_date,
        "update_date" : cft.update_date,
        "user_information": UserView(cft.uploader),
        "questions": {

        }
    }

    for question in db.session.query(ConsentFormTemplateQuestion).filter(ConsentFormTemplateQuestion.template_id == id).all():
        data["questions"][question.id] = {
            "question": question.question
        }

    # TODO: Maybe get associated Samples?

    return data