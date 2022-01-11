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

from ...database import db, Base
from ...mixins import RefAuthorMixin, RefEditorMixin
from ..enums import ConsentWithdrawalRequester


class SampleConsent(Base, RefAuthorMixin, RefEditorMixin):
    __versioned__ = {}
    identifier = db.Column(db.String(128))
    donor_id = db.Column(db.Integer, db.ForeignKey("donor.id", use_alter=True))

    comments = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False)
    undertaken_by = db.Column(db.String(128))

    study_event_id = db.Column(db.Integer, db.ForeignKey("donorprotocolevent.id"))
    study = db.relationship("DonorProtocolEvent", uselist=False)

    file_id = db.Column(db.Integer, db.ForeignKey("document.id", use_alter=True))
    file = db.relationship("Document")

    withdrawn = db.Column(db.Boolean, default=False, nullable=False)
    withdrawal_date = db.Column(db.Date)

    withdrawal_event = db.relationship(
        "SampleConsentWithdrawal",
        uselist=False,
        primaryjoin="SampleConsent.id == SampleConsentWithdrawal.consent_id",
        backref="sampleconsentwithdrawal",
    )

    future_event = db.relationship(
        "SampleConsent",
        uselist=False,
        secondary="sampleconsentwithdrawal",
        primaryjoin="SampleConsent.id == SampleConsentWithdrawal.future_consent_id",
        secondaryjoin="SampleConsent.id == SampleConsentWithdrawal.consent_id",
        backref="sampleconsentwithdrawal",
    )

    template_id = db.Column(db.Integer, db.ForeignKey("consentformtemplate.id"))

    template = db.relationship("ConsentFormTemplate", uselist=False)
    template_questions = db.relationship(
        "ConsentFormTemplateQuestion",
        uselist=True,
        secondary="consentformtemplate",
        viewonly=True,
    )

    answers = db.relationship(
        "ConsentFormTemplateQuestion",
        uselist=True,
        secondary="sampleconsentanswer",
        viewonly=True,
    )


class SampleConsentAnswer(Base, RefAuthorMixin, RefEditorMixin):
    __versioned__ = {}
    consent_id = db.Column(
        db.Integer, db.ForeignKey("sampleconsent.id", use_alter=True)
    )
    question_id = db.Column(
        db.Integer, db.ForeignKey("consentformtemplatequestion.id", use_alter=True)
    )


class SampleConsentWithdrawal(Base, RefAuthorMixin, RefEditorMixin):
    __versioned__ = {}

    consent_id = db.Column(db.ForeignKey("sampleconsent.id", use_alter=True))
    withdrawal_reason = db.Column(db.Text)

    requested_by = db.Column(db.Enum(ConsentWithdrawalRequester))

    disposal_required = db.Column(db.Boolean, nullable=False, default=True)
    future_consent = db.Column(db.Boolean, nullable=False, default=False)

    future_consent_id = db.Column(db.ForeignKey("sampleconsent.id", use_alter=True))

    file_id = db.Column(db.Integer, db.ForeignKey("document.id", use_alter=True))
    file = db.relationship("Document")

    event_id = db.Column(db.Integer, db.ForeignKey("event.id", use_alter=True))

    event = db.relationship("Event", uselist=False)
