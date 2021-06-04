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

from flask import request, current_app, jsonify, send_file, flash
from ...api import api
from ...api.generics import generic_edit, generic_lock, generic_new
from ...api.responses import *
from ...api.filters import generate_base_query_filters, get_filters_and_joins
from ...decorators import token_required
from ...webarg_parser import use_args, use_kwargs, parser
from ...database import db, SampleRack, UserAccount, EntityToStorage, \
    ColdStorageShelf, ColdStorage, Room, Building, SiteInformation

from ..enums import EntityToStorageType

from sqlalchemy.sql import insert, func
from sqlalchemy import or_, and_

from marshmallow import ValidationError

from ..views.rack import *
import requests


@api.route("/storage/rack", methods=["GET"])
@token_required
def storage_rack_home(tokenuser: UserAccount):

    return success_with_content_response(
        basic_sample_racks_schema.dump(SampleRack.query.all())
    )


@api.route("/storage/rack/LIMBRACK-<id>", methods=["GET"])
@token_required
def storage_rack_view(id, tokenuser: UserAccount):
    return success_with_content_response(
        rack_schema.dump(SampleRack.query.filter_by(id=id).first_or_404())
    )


@api.route("/storage/rack/new/", methods=["POST"])
@token_required
def storage_rack_new(tokenuser: UserAccount):
    values = request.get_json()
    return generic_new(
        db,
        SampleRack,
        new_sample_rack_schema,
        basic_sample_rack_schema,
        values,
        tokenuser,
    )


@api.route("/storage/rack/new/with_samples", methods=["POST"])
@token_required
def storage_rack_new_with_samples(tokenuser: UserAccount):

    values = request.get_json()
    print(values)
    if not values:
        return no_values_response()

    samples_pos = values.pop("samples_pos")
    entry_datetime = values.pop("entry_datetime")
    entry = values.pop("entry")

    # Step 1. Validate and add new sample rack
    try:
        result = new_sample_rack_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    new_rack = SampleRack(**result)
    new_rack.author_id = tokenuser.id
    try:
        db.session.add(new_rack)
        db.session.flush()
        rack_id = new_rack.id
        print('new_rack id: ', rack_id)

    except Exception as err:
        return transaction_error_response(err)

    # Step 2. New entitytostorage with storage_type 'STB'
    stb_batch = []
    for sample in samples_pos:
        print("sample", sample)
        sample_id = sample['sample_id']

        # Step 2.1 Delete existing entity to storage record for given sample
        #  Could consider setting removed to True instead of delete the whole record in the future
        #
        stbs = EntityToStorage.query.filter(EntityToStorage.sample_id == sample_id,
                    EntityToStorage.storage_type!='BTS').all()
                    #(EntityToStorage.removed.is_(None) | EntityToStorage.removed!=True)).all()

        if stbs is not None:
            for stb in stbs:
                print('stb', stb)
                # stb.removed = True
                # stb.editor_id = tokenuser.id;
                # stb.updated_on = func.now()
                try:
                    db.session.delete(stb)
                    #db.session.add(stb)

                except Exception as err:
                    print(err)
                    return transaction_error_response(err)

        # Step 2.2. Add new sample to rack record
        stb_values = new_sample_to_sample_rack_schema.load(sample)

        print('stb_values: ', stb_values)
        new_stb = EntityToStorage(**stb_values)
        new_stb.storage_type = 'STB'
        new_stb.author_id = tokenuser.id
        new_stb.entry_datetime = entry_datetime
        new_stb.entry = entry
        new_stb.rack_id = new_rack.id
        stb_batch.append(new_stb)

    # Postgres dialect, prefetch the id for batch insert
    identities = [
        val for val, in db.session.execute(
            "select nextval('entitytostorage_id_seq') from "
            "generate_series(1,%s)" % len(stb_batch)
    )]
    print("identities: ", identities)
    for stb_id, new_stb in zip(identities, stb_batch):
        new_stb.id = stb_id

    try:
        db.session.add_all(stb_batch)
        db.session.commit()
        flash('New Sample Rack with Samples Added Successfully!')
    except Exception as err:
        return transaction_error_response(err)

    return success_with_content_response({"id":rack_id})


@api.route("/storage/rack/LIMBRACK-<id>/lock", methods=["POST"])
@token_required
def storage_rack_lock(id, tokenuser: UserAccount):
    return generic_lock(db, SampleRack, id, basic_sample_wrack_schema, tokenuser)


@api.route("/storage/rack/LIMBRACK-<id>/edit", methods=["PUT"])
@token_required
def storage_rack_edit(id, tokenuser: UserAccount):
    # Step 1: SampleRack update
    # Step 2: If shelf_id exist, EntityToStorage update.
    values = request.get_json()
    print(values)
    if not values:
        return no_values_response()

    rack = SampleRack.query.get(id)

    if not rack:
        return not_found()

    storage_id = values['storage_id']
    shelf_id = values['shelf_id']
    values.pop('storage_id', None)
    values.pop('shelf_id', None)
    try:
        result = new_sample_rack_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    rack.update(values)
    rack.editor_id = tokenuser.id
    rack.updated_on = func.now()

    db.session.add(rack)
    print("storage_id", storage_id )
    if storage_id is not None and storage_id != '':
        storage = EntityToStorage.query.get(storage_id)
        if not storage:
            return not_found()

        storage.shelf_id = shelf_id
        storage.editor_id = tokenuser.id
        storage.updated_on = func.now()
        db.session.add(storage)

    try:
        db.session.commit()
        return success_with_content_response(values)
    except Exception as err:
        return transaction_error_response(err)


@api.route("/storage/rack/LIMBRACK-<id>/editbasic", methods=["PUT"])
@token_required
def storage_rack_edit_basic(id, tokenuser: UserAccount):
    values = request.get_json()
    return generic_edit(
        db, SampleRack, id, new_sample_rack_schema, rack_schema, values, tokenuser
    )


@api.route("/storage/rack/location/LIMBRACK-<id>", methods=["GET"])
@token_required
def storage_rack_location(id, tokenuser: UserAccount):
    results = ''

    stmt = db.session.query(SampleRack).filter_by(id=id). \
        with_entities(id, SampleRack.serial_number, SampleRack.description, SampleRack.uuid).first_or_404()

    if stmt is None:
        return success_with_content_response(results)

    results = [{'id': rackid, 'serial_number': serial_number, 'description': description,
                    'uuid': uuid, 'storage_id': None, 'shelf_id': None}
                   for (rackid, serial_number, description, uuid) in [stmt]][0]
    print("okok-", results)

    try:
        # Get shelf_id for the give rack id
        stmt = db.session.query(SampleRack).\
            outerjoin(EntityToStorage, SampleRack.id==EntityToStorage.rack_id).\
            join(ColdStorageShelf, EntityToStorage.shelf_id==ColdStorageShelf.id). \
            filter(SampleRack.id == id, EntityToStorage.storage_type == 'BTS'). \
            with_entities(EntityToStorage.id, ColdStorageShelf.id).first_or_404()

        if stmt is not None:
            shelf_results = [{'storage_id': storageid, 'shelf_id': shelfid}
                       for (storageid, shelfid) in [stmt]][0]

            results.update(shelf_results)

            print('stmt: ', stmt)

    except:
        pass

    print(results)
    return success_with_content_response(results)


@api.route("/storage/rack/shelves_onsite/LIMBRACK-<id>", methods=["GET"])
@token_required
def storage_shelves_onsite(id, tokenuser: UserAccount):
    # Get the list of shelves of the same site for a given rack id
    subq = db.session.query(SiteInformation.id).join(Building).\
            join(Room).join(ColdStorage).join(ColdStorageShelf).\
            join(EntityToStorage, EntityToStorage.shelf_id==ColdStorageShelf.id).\
            filter(EntityToStorage.rack_id == id, EntityToStorage.storage_type=='BTS')

    stmt = db.session.query(SiteInformation.id).join(Building).\
            join(Room).join(ColdStorage).join(ColdStorageShelf).\
            filter(SiteInformation.id == subq.first().id).\
            with_entities(ColdStorageShelf.id, SiteInformation.name, Building.name, Room.name,
                          ColdStorage.alias, ColdStorage.temp, ColdStorageShelf.name).\
            distinct(ColdStorageShelf.id).all()

    print('stmt: ', stmt)
    results = [{'id':shelfid,'name':'%s - %s - %s - %s (%s) - %s' % (sitename, buildingname, roomname, csname, cstemp, shelfname)}
                for (shelfid, sitename, buildingname, roomname, csname, cstemp, shelfname) in stmt]
    print(results)

    return success_with_content_response(results)


@api.route("/storage/rack/assign/sample", methods=["POST"])
@token_required
def storage_transfer_sample_to_rack(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        result = new_sample_to_sample_rack_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    # check if Sample exists.
    ets = EntityToStorage.query.filter_by(sample_id=values["sample_id"]).first()

    if not ets:
        ets = EntityToStorage(**values)
        ets.author_id = tokenuser.id
        ets.storage_type = "STB"
    else:
        ets.shelf_id = None
        ets.rack_id = None
        ets.storage_type = "STB"
        ets.update(values)
    try:
        db.session.add(ets)
        db.session.commit()
        db.session.flush()

        return success_with_content_response(
            view_sample_to_sample_rack_schema.dump(ets)
        )
    except Exception as err:
        print(">>>>>>>>>>>>>>>", err)
        return transaction_error_response(err)
