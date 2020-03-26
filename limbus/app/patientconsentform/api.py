from .views import pcf, db
from .models import ConsentFormTemplate, ConsentFormTemplateQuestion
from ..sample.models import (
    SamplePatientConsentFormTemplateAssociation,
    Sample,
    SamplePatientConsentFormAnswersAssociation,
)


@pcf.route("/api/sample/LIMBSMP-<sample_id>")
def view_pcf(sample_id):
    spcata = (
        db.session.query(SamplePatientConsentFormTemplateAssociation)
        .filter(SamplePatientConsentFormTemplateAssociation.sample_id == sample_id)
        .first_or_404()
    )
    template = (
        db.session.query(ConsentFormTemplate)
        .filter(ConsentFormTemplate.id == spcata.template_id)
        .first_or_404()
    )
    questions = (
        db.session.query(ConsentFormTemplateQuestion)
        .filter(ConsentFormTemplateQuestion.template_id == template.id)
        .all()
    )

    answers = (
        db.session.query(SamplePatientConsentFormAnswersAssociation)
        .filter(
            SamplePatientConsentFormAnswersAssociation.sample_pcf_association_id
            == spcata.id
        )
        .all()
    )

    data = {
        "template_information": {"name": template.name, "version": template.version},
        "q_and_as": {},
    }

    for q in questions:
        data["q_and_as"][q.id] = {"question": q.question, "answer": False}

        for a in answers:
            if a.checked == q.id:
                data["q_and_as"][q.id]["answer"] = True

    return data
