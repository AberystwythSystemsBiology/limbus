# Copyright (C) 2019  Keiron O'Shea <keo7@aber.ac.uk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
            "user_information": UserView(template.uploader),
        }

    return data


def PatientConsentFormView(id) -> dict:

    cft = (
        db.session.query(ConsentFormTemplate)
        .filter(ConsentFormTemplate.id == id)
        .first_or_404()
    )

    data = {
        "id": id,
        "name": cft.name,
        "version": cft.version,
        "upload_date": cft.upload_date,
        "update_date": cft.update_date,
        "user_information": UserView(cft.uploader),
        "questions": {},
    }

    for question in (
        db.session.query(ConsentFormTemplateQuestion)
        .filter(ConsentFormTemplateQuestion.template_id == id)
        .all()
    ):
        data["questions"][question.id] = {"question": question.question}

    # TODO: Maybe get associated Samples?

    return data
