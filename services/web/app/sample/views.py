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

from ..extensions import ma
import marshmallow_sqlalchemy as masql
from marshmallow import fields
from marshmallow_enum import EnumField

from ..auth.views import BasicUserAccountSchema
from ..consent.views import (
    BasicConsentFormQuestionSchema,
    BasicConsentFormTemplateSchema,
)
from ..document.views import BasicDocumentSchema
from ..protocol.views import BasicProtocolTemplateSchema

from ..database import (
    Sample,
    SampleConsent,
    SampleConsentAnswer,
    SampleProtocolEvent,
    SampleReview,
    SampleToType,
    SampleDisposal,
    SampleDocument,
)

from .enums import (
    SampleType,
    SampleStatus,
    FluidContainer,
    Colour,
    SampleSource,
    SampleQuality,
    MolecularSampleType,
    TissueSampleType,
    BiohazardLevel,
    DisposalInstruction,
    CellSampleType,
    FixationType,
    FluidSampleType,
    CellContainer,
    FluidSampleType,
    SampleType,
)


import requests
from flask import url_for
from ..misc import get_internal_api_header



