from flask import redirect, abort, render_template, url_for, session, request, jsonify
from flask_login import current_user

from ... import db
from .. import storage

from ..models import (
    Site,
    Room,
    FixedColdStorage,
    FixedColdStorageShelf,
    SampleToFixedColdStorageShelf,
    CryovialBoxToFixedColdStorageShelf,
    CryovialBox
)
from ...sample.models import Sample


@storage.route("/")
def index():
    return render_template("storage/index.html")


# TODO: Replace all of this with a sensible, granular RESTful API
@storage.route("/overview")
def overview():
    sites = db.session.query(Site).all()
    rooms = db.session.query(Room).all()
    fridges = db.session.query(FixedColdStorage).all()
    shelves = db.session.query(FixedColdStorageShelf).all()
    from pprint import pprint
    pprint(sites)

    output = {'sites': []}
    for site in sites:
        out_site = {'name': site.name,
                    'id': site.id,
                    'rooms': []}
        site_rooms = [room for room in rooms if room.site_id == site.id]
        output['sites'].append(out_site)
        for room in site_rooms:
            site_room = {'building': room.building,
                         'number': room.room_number,
                         'id': room.id,
                         'fridges': []}
            out_site['rooms'].append(site_room)
            room_fridges = [fridge for fridge in fridges if fridge.room_id == room.id]
            for fridge in room_fridges:
                room_fridge = {'serial': fridge.serial_number,
                               'manufacturer': fridge.manufacturer,
                               'id': fridge.id,
                               'shelves': []}
                site_room['fridges'].append(room_fridge)
                fridge_shelves = [shelf for shelf in shelves if shelf.storage_id == fridge.id]
                for shelf in fridge_shelves:
                    fridge_shelf = {'name': shelf.name,
                                    'id': shelf.id,
                                    'cryoboxes': [],
                                    'samples': []}
                    room_fridge['shelves'].append(fridge_shelf)
                    cryoboxes = (
                        db.session.query(CryovialBox)
                        .outerjoin(CryovialBoxToFixedColdStorageShelf, CryovialBox.id == CryovialBoxToFixedColdStorageShelf.box_id)
                        .filter(CryovialBoxToFixedColdStorageShelf.shelf_id == shelf.id)
                        .filter(CryovialBox.id == CryovialBoxToFixedColdStorageShelf.box_id)
                        .all()
                    )
                    samples = (
                        db.session.query(Sample)
                        .outerjoin(SampleToFixedColdStorageShelf, Sample.id == SampleToFixedColdStorageShelf.sample_id)
                        .filter(SampleToFixedColdStorageShelf.shelf_id == shelf.id)
                        .all()
                    )
                    for cryobox in cryoboxes:
                        fridge_shelf['cryoboxes'].append({'id': cryobox.id})
                    for sample in samples:
                        fridge_shelf['samples'].append({'id': sample.id})

    return jsonify(output), 201, {"Content-Type": "application/json"}
