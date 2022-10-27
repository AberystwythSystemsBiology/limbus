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

from sqlalchemy_continuum import (
    version_class,
    changeset,
    #transaction_class,
    #count_versions,
)
from sqlalchemy.sql import or_, func

from datetime import datetime


def func_sample_type_info(info):
    types = [
        info[key]
        for key in info
        if (key not in ["id", "author"] and info[key] is not None)
    ]
    return types


def func_transaction_summary(audit_tr):
    """
    Input: an audit trail for the same transaction
    Return: the summary description in dictionary
    with keys same as the audit trail data
    """
    # print("audit_tr", audit_tr)
    # Initialise desc1 - transaction summary
    desc1 = audit_tr[0].copy()
    desc1["object"] = "Summary"
    OperationType = {0: "Insert", 1: "Update", 2: "Delete"}

    # -- get list of object involved in the transaction
    objs = list(set([d["object"] for d in audit_tr]))
    dbids = {}
    uuids = {}
    operations = {}
    chgkeys = {}
    updates = {}
    print("objs: ", len(objs))
    # -- filling missing author/editor info
    if desc1["author"] is None:
        for d in audit_tr:
            try:
                author_id = d["author"]["id"]
            except:
                author_id = None

            if author_id is not None:
                desc1["author"] = d["author"].copy()
                break

    if desc1["editor"] is None:
        for d in audit_tr:
            try:
                editor_id = d["editor"]["id"]
            except:
                editor_id = None

            if editor_id is not None:
                desc1["editor"] = d["editor"].copy()
                break

    for object in objs:
        ds = [d["id"] for d in audit_tr if d["object"] == object]
        dbids[object] = {"count": len(ds), "DBid": ds}
        operations[object] = list(
            set([d["operation_type"] for d in audit_tr if d["object"] == object])
        )
        print("operation ", operations)
        chgks = [
            list(d["change_set"].keys()) for d in audit_tr if d["object"] == object
        ]
        # Flatten list of list
        chgks = [
            i
            for b in map(lambda x: [x] if not isinstance(x, list) else x, chgks)
            for i in b
        ]
        chgkeys[object] = list(set(chgks))

        uuids1 = [
            d["uuid"]
            for d in audit_tr
            if d["object"] == object and "uuid" in d and d["uuid"] is not None
        ]

        if len(uuids1) > 0:
            uuids[object] = uuids1
            if len(uuids[object]) > 2:
                uuids[object] = uuids[object][0:2]
                uuids[object].append("...")

        # print("uuids", uuids)

        if object == "Sample":
            updates[object] = []
            if 0 in operations[object]:  # "Insert"
                if 1 not in operations[object]:
                    smpls = [
                        (
                            func_sample_type_info(
                                d["changed_to"]["sample_type_information"]
                            )
                            + [d["changed_to"]["quantity"]]
                        )
                        for d in audit_tr
                        if d["object"] == object
                    ]
                    updates[object].append("New sample %s" % smpls)
                else:
                    updates[object].append(
                        "aliquot/derive =>(%s) subsamples"
                        % (dbids[object]["count"] - 1)
                    )
            elif 2 in operations[object]:  # "Delete"
                #smpls=[]
                smpls = [d["change_set"] for d in audit_tr if d["object"] == object]
                updates[object].append("Remove sample %s" % smpls)

            else:
                # chgks = chgkeys[object]
                # if "current_site_id" in chgks:
                #     if "status" not in chgks:
                #         updates[object].append("storage")
                #     else:
                #         updates[object].append("shipment")
                smpls = [d["change_set"] for d in audit_tr if d["object"] == object]
                if len(smpls) > 3:
                    smpls = smpls[0:3]
                    smpls.append("...")
                updates[object].append("update %s" % smpls)

        elif object == "EntityToStorage":
            ops = [OperationType[d] for d in operations[object]]
            updates[object] = ops
            storage_types = [
                d["changed_to"]["storage_type"]
                for d in audit_tr
                if d["object"] == object
            ]
            storage_types = list(set(storage_types))
            updates[object] = updates[object] + storage_types

        elif object in ["SampleProtocolEvent", "DonorProtocolEvent"]:
            ops = [OperationType[d] for d in operations[object]]
            updates[object] = ops
            protocols = [
                ": ".join(
                    (
                        d["changed_to"]["protocol"]["type"],
                        d["changed_to"]["protocol"]["name"],
                    )
                )
                for d in audit_tr
                if d["object"] == object
            ]
            protocols = list(set(protocols))  # Remove repeated protocols
            updates[object].append(protocols)

        elif object in ["Event"]:
            events = [d["change_set"] for d in audit_tr if d["object"]==object]
            updates[object] = events

        else:
            ops = [OperationType[d] for d in operations[object]]
            updates[object] = ops
            try:
                obs = [d["change_set"] for d in audit_tr if d["object"] == object]
                updates[object].append(list(set(obs)))
            except:
                pass

    # -- Sample --
    # new sample, new sample given donor consent, new sample given study reference
    # update sample basic info
    # remove sample (shallow) (deep)
    # STB: sample storage to rack
    # STS: sample storage to shelf
    # BTS: rack storage
    # Batch storage (STB):
    # Remove from storage
    # Batch Remove fromm storage
    # New sample shipment
    # Update sample shipment
    # Update sample shipment status
    # Close sample shipment
    # Update sample status
    # -- sample protocol event
    # new/update/delete sample acquisition/processing/derivation/aliquot
    # new/update/delete sample review/disposal instruction
    # batch new/update/delete sample review/disposal instruction
    #
    # -- Donor --
    # New donor
    # New donor consent
    # New donor diagnosis
    # Remove/Update donor diagnosis
    # Remove donor
    #
    # {"Sample":["New sample [['Urine', 'Other', 15.0]]"]}

    print("updates: ", updates)
    # pretty = {"call": "", "details": ""}
    # if True:
    #     keys = set(updates.keys())
    #     print(keys)
    #     if keys == {"Sample"}:
    #         info = updates["Sample"]
    #         print("info: ", info)
    #         if "new sample" in str(info).lower():
    #             pretty["call"] = "New sample"
    #             pretty["details"] = str(info).replace("[", "").replace("]", "")
    #         elif "remove" in str(info):
    #             pretty["call"] = "Remove sample"
    #             pretty["details"] = str(info).replace("[", "").replace("]", "")
    #         elif "update" in str(info):
    #             pretty["call"] = "Update sample info"
    #             pretty["details"] = str(info).replace("[", "").replace("]", "")


        # elif keys == {"Sample", "DonorProtocolEvent"}:
        #     info = updates["Sample"]
        #     pretty["call"] = ""
        #     pretty["details"] = info
        # elif keys == {"DonorProtocolEvent", "Event", "SampleConsent"}:
        #     info = updates["SampleConsent"]
        #     if "insert" in str(info).lower():
        #         pretty["call"] = "New sample consent with study reference"
        #     elif "update" in str(info).lower():
        #         pretty["call"] = "Update sample consent with study reference"
        #
        #     pretty["details"] = "Sample"

    desc1["operation_type"] = operations
    desc1["id"] = dbids
    desc1["uuid"] = uuids
    desc1["change_set"] = updates
    #desc1["details"] = pretty
    desc1.pop("changed_to", None)
    print("desc1,", desc1)
    return desc1


def func_transactions_summary(audit_trail):
    """
    Input: an audit trail
    Return: a list of summary description for each transactions in dictionary
    with keys same as the audit trail data
    """
    sorted_trail = sorted(
        audit_trail, key=lambda el: el["transaction_id"], reverse=True
    )
    tr_id = None
    desc_tr = []
    tr_ids = []

    print("Generating summary ...")
    ntr = 0
    for tr in sorted_trail + [None]:
        # print("tr:   ", tr)
        if tr is not None:
            tr_id_cur = tr["transaction_id"]
        else:
            tr_id_cur = None

        if tr_id_cur != tr_id:
            if tr_id is not None:
                # -- Get summary description
                desc1 = func_transaction_summary(audit_tr)
                desc_tr.append(desc1)
                ntr = ntr + 1
                if ntr % 100 == 0:
                    print("%d*" % ntr, end=" ")

            tr_id = tr_id_cur
            tr_ids.append(tr_id)
            audit_tr = [tr]
        else:
            audit_tr.append(tr)

    print("%d End!" % len(desc_tr))
    return desc_tr


def func_audit_trail(
    objects, start_date=None, end_date=None, user_id=None, transaction_ids=[]
):
    """
    Get the audit_trail given the filter conditions on
    Input:
        objects: list of models
        start_date, end_date
        transaction_ids: a list of transaction id
    Return:
        audit_trail for all the matched transaction records
    """
    audit_trail = []
    object_counts = {}
    audit_keys = [
        "created_on",
        "author",
        "updated_on",
        "editor",
        "operation_type",
        "transaction_id",
        "end_transaction_id",
        "id",
        "uuid",
        "object",
    ]

    print("objects", objects)
    for model in objects:
        ModelVersion = version_class(eval(model))
        if len(transaction_ids) > 0:
            stmt = (
                db.session.query(ModelVersion)
                .filter(ModelVersion.transaction_id.in_(transaction_ids))
                .filter(
                    func.date(ModelVersion.updated_on) >= start_date,
                    func.date(ModelVersion.updated_on) <= end_date,
                )
            )
            print("stmt0 ", stmt.count())
        else:
            stmt = db.session.query(ModelVersion).filter(
                func.date(ModelVersion.updated_on) >= start_date,
                func.date(ModelVersion.updated_on) <= end_date,
            )
            print("stmt1 ", stmt.count())
        if user_id:
            stmt = stmt.filter(
                or_(
                    ModelVersion.editor_id == user_id, ModelVersion.author_id == user_id
                )
            )

        res = stmt.all()
        object_counts[model] = len(res)

        # try:
        #     schema = eval("AuditBasic%sSchema(many=True)" % model)
        # except:
        #     schema = eval("Audit%sSchema(many=True)" % model)
        # audit_trail = audit_trail + schema.dump(res)
        try:
            schema = eval("AuditBasic%sSchema(many=False)" % model)
        except:
            schema = eval("Audit%sSchema(many=False)" % model)

        for obj in res:
            # a bit slow to dump objects sequentially if num of obj is large
            chgset = obj.changeset

            chgset.pop("created_on", None)
            chgset.pop("updated_on", None)
            chgset.pop("author_id", None)
            chgset.pop("editor_id", None)
            #if len(chgset) == 0:
            #    continue

            chgset = {
                key: "[%s -> %s]" % (chgset[key][0], chgset[key][1]) for key in chgset
            }

            # -- Get transaction and updated object data
            obj_dump0 = schema.dump(obj)
            chgto = {}
            obj_dump = {}
            for key in obj_dump0:
                if key in audit_keys:
                    obj_dump[key] = obj_dump0[key]
                else:
                    chgto[key] = obj_dump0[key]
            # obj_dump = {key: obj_dump0[key] for key in audit_keys if key in obj_dump0}
            obj_dump["change_set"] = chgset
            obj_dump["changed_to"] = chgto
            # obj_dump["object"] = model
            audit_trail.append(obj_dump)

        print("len trails %s %s" % (model, len(res)))

    return audit_trail, object_counts


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

    print("objects : ", type(objects), objects)
    if type(objects) == str:
        objects = objects.split(",")
    elif objects is None:
        # objects = [
        #     "Sample",
        #     "SampleProtocolEvent",
        #     "EntityToStorage",
        #     "SampleReview",
        #     "SampleDisposal",
        #     "Donor",
        #     "DonorProtocolEvent",
        #     "Event",
        # ]
        objects = [d[0] for d in GeneralObject.choices()]

    print("objects : ", objects)
    start_date = args.pop("start_date", datetime.today())
    end_date = args.pop("end_date", datetime.today())
    report_type = AuditTypes[audit_type].value

    transaction_ids = []
    audit_trail = []

    uuid_model = None
    sample_id = None
    if uuid:
        # -- Get all transaction ids involving uuid
        for model in objects:
            ModelVersion = version_class(eval(model))

            try:
                transactions = (
                    db.session.query(ModelVersion)
                    .filter_by(uuid=uuid)
                    .with_entities(ModelVersion.transaction_id, ModelVersion.id)
                    .all()
                )

                if len(transactions) > 0:
                    transaction_ids = [d[0] for d in transactions]
                    uuid_model = model
                    if model == "Sample":
                        sample_id = transactions[0][1]

                    break
            except:
                pass

        if sample_id:
            # get transactions involving samples given sample_id
            for model in objects:
                if model == uuid_model:
                    continue
                try:
                    transactions = (
                        db.session.query(ModelVersion)
                        .filter_by(sample_id=sample_id)
                        .with_entities(ModelVersion.transaction_id, ModelVersion.id)
                        .all()
                    )
                    if len(transactions) > 0:
                        transaction_ids1 = [d[0] for d in transactions]
                        transaction_ids = list(set(transaction_ids + transaction_ids1))
                except:
                    pass

        if uuid_model:
            report_type = "%s (involving %s %s)" % (report_type, uuid_model, uuid)
            audit_trail, object_counts = func_audit_trail(
                objects, start_date, end_date, user_id, transaction_ids
            )
        else:
            report_type = "%s (%s !!not found!!)" % (report_type, uuid)
            object_counts = {}

    else:
        audit_trail, object_counts = func_audit_trail(
            objects, start_date, end_date, user_id
        )

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

    # -- Get summary description of transactions
    if len(audit_trail) > 0:
        try:
            desc_trail = func_transactions_summary(audit_trail)
            for d in audit_trail:
                d.pop("changed_to", None)

            audit_trail = audit_trail + desc_trail
        except:
            for d in audit_trail:
                d.pop("changed_to", None)

    return success_with_content_response({"data": audit_trail, "title": title})


@api.route("/audit/sample/<uuid>", methods=["GET"])
@token_required
def audit_sample(uuid: str, tokenuser: UserAccount):
    if not tokenuser.is_admin:
        return not_allowed()

    SampleVersion = version_class(Sample)
    sample_trail = db.session.query(SampleVersion).filter_by(uuid=uuid).all()
    # n=1
    # for ver in sample_trails:
    #     print("ver ver.changeset: ", ver.changeset)
    #     n=n+1

    print("version count: ", n)
    audit_trail = audit_samples_schema.dump(sample_trail)
    # -- Need to get relevant objects involved in the same transaction:
    # protocol events: review, disposal, consent etc.
    #
    return success_with_content_response(audit_trail)
