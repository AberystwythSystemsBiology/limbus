from flask import redirect, abort, render_template, url_for, session, request, jsonify
from flask_login import current_user

from ... import db
from .. import storage

from ..models import (
    Site,
    Room,
    FixedColdStorage,
    FixedColdStorageShelf,
    EntityToStorage,
)


@storage.route("/")
def index():
    return render_template("storage/index.html")


from ..enums import EntityToStorageTpye
from ..models import EntityToStorage


def move_entity_to_storage(
    sample_id: int = None,
    box_id: int = None,
    shelf_id: int = None,
    row: int = None,
    col: int = None,
    entered=None,
    entered_by=None,
    author_id: int = None,
    storage_type: EntityToStorageTpye = None,
) -> None:

    if storage_type in [EntityToStorageTpye.STB, EntityToStorageTpye.STS]:
        r = (
            db.session.query(EntityToStorage)
            .filter(EntityToStorage.sample_id == sample_id)
            .first()
        )
    elif storage_type == EntityToStorageTpye.BTS:
        r = (
            db.session.query(EntityToStorage)
            .filter(EntityToStorage.box_id == box_id)
            .first()
        )

    if r != None:
        r.sample_id = sample_id
        r.box_id = box_id
        r.shelf_id = shelf_id
        r.row = row
        r.col = col
        r.entered = entered
        r.entered_by = entered_by
        r.author_id = author_id
        r.storage_type = storage_type
    else:
        r = EntityToStorage(
            sample_id=sample_id,
            box_id=box_id,
            shelf_id=shelf_id,
            row=row,
            col=col,
            storage_type=storage_type,
            entered=entered,
            entered_by=entered_by,
            author_id=author_id,
        )
        db.session.add(r)

    db.session.commit()


# TODO: Replace all of this with a sensible, granular RESTful API (lol)
@storage.route("/overview")
def overview():
    sites = db.session.query(Site).all()
    rooms = db.session.query(Room).all()
    fridges = db.session.query(FixedColdStorage).all()
    shelves = db.session.query(FixedColdStorageShelf).all()

    output = {"sites": []}
    for site in sites:
        out_site = {"name": site.name, "id": site.id, "rooms": []}
        site_rooms = [room for room in rooms if room.site_id == site.id]
        output["sites"].append(out_site)
        for room in site_rooms:
            site_room = {
                "building": room.building,
                "number": room.room_number,
                "id": room.id,
                "fridges": [],
            }
            out_site["rooms"].append(site_room)
            room_fridges = [fridge for fridge in fridges if fridge.room_id == room.id]
            for fridge in room_fridges:
                room_fridge = {
                    "serial": fridge.serial_number,
                    "manufacturer": fridge.manufacturer,
                    "id": fridge.id,
                    "shelves": [],
                }
                site_room["fridges"].append(room_fridge)
                fridge_shelves = [
                    shelf for shelf in shelves if shelf.storage_id == fridge.id
                ]
                for shelf in fridge_shelves:
                    fridge_shelf = {
                        "name": shelf.name,
                        "id": shelf.id,
                        "cryoboxes": [],
                        "samples": [],
                    }
                    room_fridge["shelves"].append(fridge_shelf)

    return jsonify(output), 201, {"Content-Type": "application/json"}
