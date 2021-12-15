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

from flask import request, abort, url_for, flash, jsonify
from marshmallow import ValidationError
from sqlalchemy.sql import func

from ...api import api, generics
from ...api.responses import *
from ...api.filters import generate_base_query_filters, get_filters_and_joins

from ...decorators import token_required, check_if_admin
from ...misc import get_internal_api_header
from ...webarg_parser import use_args, use_kwargs, parser

from ..views import (
    basic_samples_schema,
    basic_sample_schema,
    sample_schema, #sample_view_schema,
    samples_schema,
    #audit_samples_schema,
    SampleFilterSchema,
    new_fluid_sample_schema,
    sample_type_schema,
    new_cell_sample_schema,
    new_molecular_sample_schema,
    new_sample_schema, edit_sample_schema,
    sample_types_schema
)

from ..views.audit import audit_samples_schema, audit_sample_protocol_events_schema
from ...database import (db, Sample, SampleToType, SubSampleToSample, UserAccount, Event,
                         SampleProtocolEvent, ProtocolTemplate, SampleReview, DonorProtocolEvent,
                         SampleDisposalEvent, SampleDisposal,
                         UserCart, SampleShipment, SampleShipmentToSample, SampleShipmentStatus,
                         EntityToStorage,
                         SiteInformation, Building, Room, ColdStorage, ColdStorageShelf,
                         SampleConsent, DonorToSample, SampleToCustomAttributeData,
                         SampleConsentAnswer, ConsentFormTemplateQuestion)

from ..enums import *
from ...protocol.enums import ProtocolType

import requests

from sqlalchemy_continuum import version_class, Operation, changeset
from sqlalchemy_continuum import transaction_class
from sqlalchemy_continuum.utils import count_versions, is_modified

@api.route("/sample/<uuid>/audit", methods=["GET"])
def sample_audit(uuid:str):
    SampleVersion = version_class(Sample)
    sample_trails = db.session.query(SampleVersion).filter_by(uuid=uuid).all()

    column_keys = SampleVersion.__table__.columns.keys()
    print(column_keys)
    audit_trails = audit_samples_schema.dump(sample_trails)

    return success_with_content_response(audit_trails)



@api.route("/sample/audit/<start_date>/<end_date>", methods=["GET"])
@api.route("/sample/audit/<start_date>", methods=["GET"])
def sample_audit_period(start_date, end_date=None):
    print("===> start:", start_date, " ; end:", end_date)
    SampleVersion = version_class(Sample)
    if end_date:
        sample_trails = db.session.query(SampleVersion).filter(SampleVersion.updated_on >= start_date, SampleVersion.updated_on<end_date).all()
    else:
        sample_trails = db.session.query(SampleVersion).filter(SampleVersion.updated_on == start_date).all()

    print("llen sample trails", len(sample_trails))
    #
    # column_keys = SampleVersion.__table__.columns.keys()
    # print(column_keys)
    audit_trails = audit_samples_schema.dump(sample_trails)

    return success_with_content_response(audit_trails)


@api.route("/sample/<uuid>/audit/protocol_envent", methods=["GET"])
def protocol_event_audit(uuid: str):
    SampleVersion = version_class(Sample)
    ProtocolEventVersion = version_class(SampleProtocolEvent)
    pe_trails = db.session.query(ProtocolEventVersion) \
        .join(SampleVersion, ProtocolEventVersion.sample_id == SampleVersion.id) \
        .filter(SampleVersion.uuid == uuid)

    pe_trails1 = db.session.query(ProtocolEventVersion) \
        .join(SubSampleToSample, ProtocolEventVersion.sample_id == SubSampleToSample.parent_id) \
        .join(SampleVersion, SubSampleToSample.subsample_id == SampleVersion.id) \
        .filter(SampleVersion.uuid == uuid) \
        .filter(SubSampleToSample.protocol_event_id == ProtocolEventVersion.id)

    pe_trails = pe_trails.union(pe_trails1).all()

    column_keys = ProtocolEventVersion.__table__.columns.keys()
    print(column_keys)
    audit_trails = audit_sample_protocol_events_schema.dump(pe_trails)
    return success_with_content_response(audit_trails)


@api.route("/sample/<uuid>/audit/storage", methods=["GET"])
def sample_storage_audit(uuid: str):
    SampleVersion = version_class(Sample)
    ProtocolEventVersion = version_class(SampleProtocolEvent)
    pe_trails = db.session.query(ProtocolEventVersion) \
        .join(SampleVersion, ProtocolEventVersion.sample_id == SampleVersion.id) \
        .filter(SampleVersion.uuid == uuid)

    pe_trails1 = db.session.query(ProtocolEventVersion) \
        .join(SubSampleToSample, SubSampleToSample.protocol_event_id == ProtocolEventVersion.id) \
        .join(SampleVersion, SubSampleToSample.subsample_id == SampleVersion.id) \
        .filter(SampleVersion.uuid == uuid) \

    pe_trails = pe_trails.union(pe_trails1).all()

    column_keys = ProtocolEventVersion.__table__.columns.keys()
    print(column_keys)
    audit_trails = audit_sample_protocol_events_schema.dump(pe_trails)
    return success_with_content_response(audit_trails)

