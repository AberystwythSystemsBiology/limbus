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

from ..api import api
from ..api.responses import *
from ..decorators import token_required
from ..webarg_parser import use_args, use_kwargs, parser

from ..database import db, Sample, SubSampleToSample, UserAccount, SampleProtocolEvent
from ..admin.views import *  # audit_samples_schema, audit_sample_protocol_events_schema
from ..admin.enums import *

from sqlalchemy_continuum import version_class
from sqlalchemy.sql import or_, func

from datetime import datetime


@api.route("/audit/query", methods=["GET"])
@use_args(AuditFilterSchema(), location="json")
@token_required
def audit_query(args, tokenuser: UserAccount):

    print("args", args)
    if not tokenuser.is_admin:
        return not_allowed()

    user_id = args.pop("user_id", None)
    uuid = args.pop("uuid", None)

    audit_type = args.pop("audit_type", None)
    if audit_type == "GEN":
        objects = args.pop("general_object", None)
    elif audit_type == "SMP":
        objects = args.pop("sample_object", None)
    elif audit_type == "DNR":
        objects = args.pop("donor_object", None)
    elif audit_type == "SOP":
        objects = args.pop("template_object", None)
    elif audit_type == "AUT":
        objects = args.pop("auth_object", None)
    elif audit_type == "LTS":
        objects = args.pop("storage_object", None)
    else:
        objects = None

    if type(objects) == str:
        objects = objects.split(",")
    elif objects is None:
        objects = [
            "Sample",
            "SampleProtocolEvent",
            "EntityToStorage",
            "SampleReview",
            "SampleDisposal",
            "Donor",
            "DonorProtocolEvent",
        ]

    print("objects:", objects)
    start_date = args.pop("start_date", datetime.now())
    end_date = args.pop("end_date", datetime.now())
    audit_trails = []
    object_counts = {}
    for model in objects:
        if model == "EntityToStorage":
            ModelVersion = eval(model)
        else:
            ModelVersion = version_class(eval(model))

        stmt = db.session.query(ModelVersion).filter(
            ModelVersion.updated_on >= start_date, ModelVersion.updated_on <= end_date
        )

        if user_id:
            stmt = stmt.filter(
                or_(
                    ModelVersion.editor_id == user_id, ModelVersion.author_id == user_id
                )
            )
        if uuid:
            try:
                stmt = stmt.filter_by(uuid=uuid)
            except:
                pass

        res = stmt.all()
        object_counts[model] = len(res)

        print("len trails %s %s" % (model, len(res)))
        try:
            schema = eval("AuditBasic%sSchema(many=True)" % model)
        except:
            schema = eval("Audit%sSchema(many=True)" % model)

        audit_trails = audit_trails + schema.dump(res)

    report_type = AuditTypes[audit_type].value

    if uuid:
        report_type = "%s: %s" % (report_type, uuid)

    if user_id == 0:
        report_user = "Not Specified"

    else:
        user = UserAccount.query.filter_by(id=user_id).first()
        if user:
            report_user = "%s %s (%s)" % (user.first_name, user.last_name, user.email)
        else:
            report_user = "Not Found"

    title = {
        "report_type": report_type,
        "report_start_date": start_date,
        "report_end_date": end_date,
        "report_objects": objects,
        "report_object_counts": object_counts,
        "report_user": report_user,
        "report_created_by": "%s %s (%s)"
        % (tokenuser.first_name, tokenuser.last_name, tokenuser.email),
        "report_created_on": datetime.now(),
    }

    return success_with_content_response({"data": audit_trails, "title": title})


@api.route("/audit/sample/<uuid>", methods=["GET"])
@token_required
def audit_sample(uuid: str, tokenuser: UserAccount):
    if not tokenuser.is_admin:
        return not_allowed()

    SampleVersion = version_class(Sample)
    sample_trails = db.session.query(SampleVersion).filter_by(uuid=uuid).all()

    column_keys = SampleVersion.__table__.columns.keys()
    print(column_keys)
    audit_trails = audit_samples_schema.dump(sample_trails)

    return success_with_content_response(audit_trails)
