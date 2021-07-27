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
from __future__ import print_function

from flask import request, current_app, jsonify, send_file, flash, url_for
from ...api import api
from ...misc import get_internal_api_header
from ...api.generics import generic_edit, generic_lock, generic_new
from ...api.responses import *
from ...api.filters import generate_base_query_filters, get_filters_and_joins
from ...decorators import token_required
from ...webarg_parser import use_args, use_kwargs, parser
from ...database import db, SampleRack, UserAccount, EntityToStorage, \
    ColdStorageShelf, ColdStorage, Room, Building, SiteInformation,Sample,UserCart

from ..enums import EntityToStorageType

from sqlalchemy.sql import insert, func
from sqlalchemy import or_, and_, not_

from marshmallow import ValidationError

from ..views.rack import *
import requests
from itertools import product


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
    #print(values)
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
    for sample in samples_pos:
        sample['entry_datetime'] = entry_datetime
        sample['entry'] = entry

    # insert confirmed data to database
    return func_transfer_samples_to_rack(
        samples_pos, rack_id, tokenuser
    )


def func_transfer_samples_to_rack(samples_pos, rack_id, tokenuser: UserAccount):
    # Update entitytostorage with storage_type 'STB'
    stb_batch = []
    for sample in samples_pos:
        #print("sample", sample)
        sample_id = sample['sample_id']

        # Step 1 Delete existing entity to storage record for given sample
        #  ??Could consider setting removed to True instead of delete the whole record in the future
        #
        stbs = EntityToStorage.query.filter(EntityToStorage.sample_id == sample_id,
                    EntityToStorage.storage_type!='BTS',
                    or_(EntityToStorage.removed.is_(None), EntityToStorage.removed != True)).all()

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

        # Step 2. Add new sample to rack record
        # stb_values = {'sample_id': sample['sample_id'], 'row': sample['row'], 'col': sample['col'],
        #               'rack_id': rack_id, 'storage_type': 'STB'}

        stb_values = new_sample_to_sample_rack_schema.load(sample, unknown = 'EXCLUDE')

        new_stb = EntityToStorage(**stb_values)
        new_stb.storage_type = 'STB'
        new_stb.author_id = tokenuser.id
        new_stb.rack_id = rack_id
        if 'entry_datetime' not in sample:
            new_stb.entry_datetime = func.now()
        # if 'entry' not in sample:
        #     sample.entry = tokenuser.first_name[0]+tokenuser.last_name[0]
        stb_batch.append(new_stb)

    # Postgres dialect, prefetch the id for batch insert
    identities = [
        val for val, in db.session.execute(
            "select nextval('entitytostorage_id_seq') from "
            "generate_series(1,%s)" % len(stb_batch)
    )]
    # print("identities: ", identities)
    for stb_id, new_stb in zip(identities, stb_batch):
        new_stb.id = stb_id

    try:
        db.session.add_all(stb_batch)
        db.session.commit()
        flash('Sample stored to rack Successfully!')
        message = "Sample(s) stored to rack Successfully!"
    except Exception as err:
        return transaction_error_response(err)

    return success_with_content_message_response({"id":rack_id}, message)


def func_rack_vacancies(num_rows, num_cols, occupancies=None):
    vacancies=[(i,j) for i,j in
               product(range(1,num_rows+1), range(1,num_cols+1))
               if (i,j) not in occupancies]
    return(vacancies)

def func_rack_fill_with_samples(samples, num_rows, num_cols, vacancies):
    # TO DO: allow change of fillopt
    fillopt = {'column_first': True, 'num_channels': 0}

    n_samples = len(samples)
    try:
        pos = [(samples[k]['row'], samples[k]['col']) for k in range(n_samples)]
        return(samples)
    except:
        pass

    k = 0;

    if fillopt['column_first']:
        for col in range(1, num_cols+1):
            channel_cnt = 0
            col_pos = [(j, col) for j in range(1,num_rows + 1)]
            if fillopt['num_channels']>0:
                # If the row is not fully empty, skip this row
                if len(set(col_pos).intersect(set(vacancies)))>0:
                    continue

            for row in range(1, num_rows + 1):
                if k == n_samples:
                    col = num_cols
                    break

                if (row, col) in vacancies:
                    samples[k].update({'row': row, 'col': col, 'pos': (row, col)})
                    k = k + 1;
                    channel_cnt = channel_cnt + 1;
                    if channel_cnt == fillopt['num_channels']:
                        row = num_rows; # go for next row
                elif fillopt['num_channels']>0:
                    row = num_rows; # go for next row

    else:
        for row in range(1, num_rows+1):
            channel_cnt = 0
            row_pos = [(row,j) for j in range(1,num_cols + 1)]
            if fillopt['num_channels']>0:
                # If the row is not fully empty, skip this row
                if len(set(row_pos).intersect(set(vacancies)))>0:
                    continue

            for col in range(1, num_cols + 1):
                if k == n_samples:
                    row = num_rows
                    break

                if (row, col) in vacancies:
                    sample_id = samples[k]['id']
                    samples[k].update({'row': row, 'col': col})
                    k = k + 1;
                    channel_cnt = channel_cnt + 1;
                    if channel_cnt == fillopt['num_channels']:
                        col = num_cols  # go for next row
                elif fillopt['num_channels']>0:
                    col = num_cols # go for next row

    return(samples)


@api.route("/storage/rack/fill_with_samples", methods=["POST", "GET"])
@token_required
def storage_rack_fill_with_samples(tokenuser: UserAccount):
    if request.method == 'POST':
      values = request.get_json()
      #print('request data', values)
      samples = values['samples']

    else:
        values = None

    if not values:
        return no_values_response()

    # samples_pos = values.pop("samples_pos")
    # entry_datetime = values.pop("entry_datetime")
    # entry = values.pop("entry")

    rack_id = int(values['rack_id'])
    samples = values['samples']
    commit = False
    if 'commit' in values and values['commit']:
        commit = True

    # Step 1. Validate and add new sample rack
    rack = SampleRack.query.filter_by(id=rack_id).first()
    if rack is None:
        err = {'messages':'Rack not found!'}
        return validation_error_response(err)

    if not commit:
        stbs = EntityToStorage.query.\
            filter(EntityToStorage.rack_id==rack_id, EntityToStorage.storage_type=='STB',
                   or_(EntityToStorage.removed.is_(None), EntityToStorage.removed!=True)).all()
        #print("stbs", stbs)
        occupancies = [(stb1.row, stb1.col) for stb1 in stbs]

        num_rows = rack.num_rows
        num_cols = rack.num_cols
        # Check if fully occupied
        vacancies = func_rack_vacancies(num_rows, num_cols, occupancies)
        if len(vacancies) < len(values['samples']):
            err = {'messages':'Insufficient available positions in the selected rack!'}
            return validation_error_response(err)

        sample_ids = [sample['id'] for sample in samples]
        stbs = EntityToStorage.query.\
            filter(EntityToStorage.sample_id.in_(sample_ids), EntityToStorage.storage_type=='STB',
                   or_(EntityToStorage.removed.is_(None), EntityToStorage.removed!=True)).all()
        print("stbs", [(stb1.sample_id, stb1.rack_id) for stb1 in stbs])
        sample_ids_stored0 = [stb1.sample_id for stb1 in stbs if stb1.rack_id == rack_id]
        sample_ids_stored1 = [stb1.sample_id for stb1 in stbs if stb1.rack_id != rack_id]
        n_stored1 = len(sample_ids_stored1)
        print('sample_ids_stored0 ', sample_ids_stored0)
        samples = [sample for sample in samples if sample['id'] not in sample_ids_stored0]

        message = ''
        print('n_stored1', n_stored1)
        if (n_stored1>0):
            message = "%d sample(s) already stored in a different rack, " \
                      "submit will change the location for these samples" % n_stored1

        try:
            samples = func_rack_fill_with_samples(samples, num_rows, num_cols, vacancies)
        except:
            err = {'messages': "Errors in assigning a rack position to samples!"}
            return validation_error_response(err)

        return success_with_content_message_response(samples, message)

    samples_pos = [{'sample_id': sample['id'], 'row': sample['row'], 'col': sample['col']}
                   for sample in samples]
    # insert confirmed data to database
    return func_transfer_samples_to_rack(
        samples_pos, rack_id, tokenuser
    )

@api.route("/storage/rack/LIMBRACK-<id>/query/rack",methods=["GET"])
@token_required
def storage_rack_to_shelf_check(id,tokenuser:UserAccount):
    ets = EntityToStorage.query.filter_by(rack_id=id, sample_id=None).first()
    if ets is not None:
        return success_with_content_response("RST")
    uc = UserCart.query.filter_by(rack_id=id).first()
    if uc is not None:
        return success_with_content_response("RCT")
    return success_with_content_response("RIV")

@api.route("/storage/rack/LIMBRACK-<id>/query/sample",methods=["GET"])
@token_required
def storage_sample_to_rack_check(id,tokenuser:UserAccount):
    ets = EntityToStorage.query.filter_by(sample_id=id).first()
    return success_with_content_response(ets is not None)


@api.route("/storage/rack/LIMBRACK-<id>/lock", methods=["POST"])
@token_required
def storage_rack_lock(id, tokenuser: UserAccount):
    return generic_lock(db, SampleRack, id, basic_sample_rack_schema, tokenuser)


@api.route("/storage/rack/LIMBRACK-<id>/edit", methods=["PUT"])
@token_required
def storage_rack_edit(id, tokenuser: UserAccount):
    # Step 1: SampleRack update
    # Step 2: If shelf_id exist, EntityToStorage update.
    values = request.get_json()
    #print('values: ', values)
    if not values:
        return no_values_response()

    rack = SampleRack.query.get(id)

    if not rack:
        return not_found()

    storage_id = values['storage_id']
    shelf_id = values['shelf_id']
    values.pop('storage_id')
    values.pop('shelf_id')
    try:
        result = new_sample_rack_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    rack.update(values)
    rack.editor_id = tokenuser.id
    rack.updated_on = func.now()

    try:
        db.session.add(rack)
        db.session.commit()
        flash('Rack basic info edited!')
    except Exception as err:
        return transaction_error_response(err)

    # print("storage_id", storage_id )

    stored = False
    if storage_id is not None and storage_id != '':
        storage = EntityToStorage.query.get(storage_id)
        if storage is not None:
            stored = True

    if stored:
        storage.shelf_id = shelf_id
        storage.editor_id = tokenuser.id
        storage.updated_on = func.now()

    else:
        # New EntityToStoarage
        storage_values = {'shelf_id': shelf_id, 'rack_id': rack.id, 'storage_type': 'BTS'}
        storage = EntityToStorage(**storage_values)
        storage.author_id = tokenuser.id
        # TO DO: add entry date time and by to form
        storage.entry_datetime = func.now()

    try:
        db.session.add(storage)
        db.session.commit()
        flash('Rack storage shelf updated!')
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

@api.route("/storage/RACK/LIMBRACK-<id>/delete", methods=["POST"])
@token_required
def storage_rack_delete(id, tokenuser: UserAccount):
    rackTableRecord = SampleRack.query.filter_by(id=id).first()
    entityStorageTableRecord = EntityToStorage.query.filter(EntityToStorage.rack_id==id).all()

    if not rackTableRecord:
        return not_found()

    if rackTableRecord.is_locked:
        return locked_response()

    rackTableRecord.editor_id = tokenuser.id
    if not entityStorageTableRecord:
        try:
            db.session.delete(rackTableRecord)
            db.session.commit()
            return success_with_content_response(None)
        except Exception as err:
            return transaction_error_response(err)
    shelfID = entityStorageTableRecord[0].shelf_id

    response = func_rack_delete(rackTableRecord,entityStorageTableRecord)
    if response == "success":
        return success_with_content_response(shelfID)
    return sample_assigned_delete_response()

#change to func_rack_delete
def func_rack_delete(record,entityStorageTableRecord):
    for ESRecord in entityStorageTableRecord:
        if not ESRecord.sample_id is None:
            return "has sample"
        db.session.delete(ESRecord)

    try:
        db.session.flush()
        db.session.delete(record)
        db.session.commit()
        return "success"
    except Exception as err:
        return transaction_error_response(err)


@api.route("/storage/rack/location/LIMBRACK-<id>", methods=["GET"])
@token_required
def storage_rack_location(id, tokenuser: UserAccount):
    # Get shelf_id for the give rack id
    stmt = db.session.query(SampleRack).filter(SampleRack.id == id).\
            with_entities(SampleRack.id, SampleRack.serial_number,
            SampleRack.description, SampleRack.uuid)

    if stmt.count() > 0:
        result = [{'id': rackid, 'serial_number': serial_number, 'description': description,
                'uuid': uuid, 'storage_id': None, 'shelf_id': None}
               for (rackid, serial_number, description, uuid) in [stmt.first()]][0]

        stmt1 = db.session.query(SampleRack).\
            join(EntityToStorage, SampleRack.id==EntityToStorage.rack_id).\
            join(ColdStorageShelf, and_(EntityToStorage.shelf_id==ColdStorageShelf.id,
                       EntityToStorage.storage_type == 'BTS')). \
            filter(SampleRack.id == id, or_(EntityToStorage.removed==None, EntityToStorage.removed==False) ).with_entities(EntityToStorage.id, EntityToStorage.shelf_id)

        if stmt1.count() > 0:
            result1 = [{'storage_id': storage_id, 'shelf_id': shelf_id}
                       for (storage_id, shelf_id) in [stmt1.first()]][0]
            result.update(result1)

    return success_with_content_response(result)



@api.route("/storage/rack/shelves_onsite/LIMBRACK-<id>", methods=["GET"])
@token_required
def storage_shelves_onsite(id, tokenuser: UserAccount):
    # Get the list of shelves of the same site for a given rack id
    # if rack id is None, then list the shelves from the same site of the user site

    if id is not None:
        subq = db.session.query(SiteInformation.id).join(Building).\
                join(Room).join(ColdStorage).join(ColdStorageShelf).\
                join(EntityToStorage, EntityToStorage.shelf_id==ColdStorageShelf.id).\
                filter(EntityToStorage.rack_id == id, EntityToStorage.storage_type=='BTS')

        stored = subq.count()>0
        if stored:
            stmt = db.session.query(SiteInformation.id).join(Building).\
                    join(Room).join(ColdStorage).join(ColdStorageShelf).\
                    filter(SiteInformation.id == subq.first().id, ~ColdStorageShelf.is_locked).\
                    with_entities(ColdStorageShelf.id, SiteInformation.name, Building.name, Room.name,
                                  ColdStorage.alias, ColdStorage.temp, ColdStorageShelf.name).\
                    distinct(ColdStorageShelf.id).all()

    if id is None or not stored:
        stmt = db.session.query(SiteInformation.id).join(Building).\
                join(Room).join(ColdStorage).join(ColdStorageShelf).\
                filter(or_(SiteInformation.id==tokenuser.site_id, tokenuser.site_id==None),
                       ~ColdStorageShelf.is_locked).\
                with_entities(ColdStorageShelf.id, SiteInformation.name, Building.name, Room.name,
                              ColdStorage.alias, ColdStorage.temp, ColdStorageShelf.name).\
                distinct(ColdStorageShelf.id).all()

    results = [{'id':shelfid,'name':'%s - %s - %s - %s (%s) - %s' % (sitename, buildingname, roomname, csname, cstemp, shelfname)}
                for (shelfid, sitename, buildingname, roomname, csname, cstemp, shelfname) in stmt]
    #print(results)

    return success_with_content_response(results)


@api.route("/storage/rack/info", methods=["GET"])
@token_required
def storage_rack_info(tokenuser: UserAccount):
    # Get the list of racks of the same site for a given rack id
    stmt = db.session.query(SampleRack).outerjoin(EntityToStorage,
         and_(SampleRack.id == EntityToStorage.rack_id,EntityToStorage.storage_type == 'BTS')).\
         outerjoin(ColdStorageShelf,EntityToStorage.shelf_id==ColdStorageShelf.id). \
         outerjoin(ColdStorage, ColdStorageShelf.storage_id==ColdStorage.id). \
         outerjoin(Room, ColdStorage.room_id==Room.id).\
         outerjoin(Building, Room.building_id==Building.id).\
         outerjoin(SiteInformation, and_(Building.site_id==SiteInformation.id, Building.site_id==tokenuser.site_id)).\
         filter(~SampleRack.is_locked).\
         with_entities(SampleRack.id,
            SampleRack.num_rows, SampleRack.num_cols,SampleRack.serial_number,  SampleRack.description,
            ColdStorageShelf.id, SiteInformation.name, Building.name, Room.name,
            ColdStorage.alias, ColdStorage.temp, ColdStorageShelf.name). \
            distinct(SampleRack.id).all()

    results = [{'id': rackid, 'num_rows': num_rows, 'num_cols': num_cols, 'serial_number': serial_number,
                'description': description or '',
                'location': '%s - %s - %s - %s (%s) - %s' %
        (sitename or '', buildingname or '', roomname or '', csname or '', cstemp or '', shelfname or '')}
            for (rackid, num_rows, num_cols, serial_number, description,
                 shelfid, sitename, buildingname, roomname, csname, cstemp, shelfname) in stmt]


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

# @api.route("/storage/rack/LIMBRACK-<id>/lock", methods=["PUT"])
# @token_required
# def storage_rack_lock(id, tokenuser: UserAccount):
#
#     rack = SampleRack.query.filter_by(id=id).first()
#
#     if not rack:
#         return not_found()
#
#     # Updates the attribute
#     rack.is_locked = not rack.is_locked
#     rack.editor_id = tokenuser.id
#
#     try:
#         db.session.commit()
#         db.session.flush()
#         return success_with_content_response(rack.is_locked)
#     except Exception as err:
#         return transaction_error_response(err)
