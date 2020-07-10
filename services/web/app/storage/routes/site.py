from flask import redirect, abort, render_template, url_for, session, request, jsonify

from flask_login import current_user, login_required
from ... import db
from .. import storage

from ..forms import SiteRegistrationForm, RoomRegistrationForm

from ..models import (
    Site,
    Room,
    FixedColdStorage,
    FixedColdStorageShelf,
)

from ...misc.models import Address
from ...auth.models import User


@storage.route("sites/")
@login_required
def site_index():
    sites = db.session.query(Site, User).filter(Site.author_id == User.id).all()
    return render_template("storage/site/index.html", sites=sites)


@storage.route("sites/new", methods=["GET", "POST"])
@login_required
def add_site():
    form = SiteRegistrationForm()
    if form.validate_on_submit():

        addr = Address(
            street_address_one=form.address_line_one.data,
            street_address_two=form.address_line_two.data,
            city=form.city.data,
            county=form.county.data,
            post_code=form.post_code.data,
            country=form.country.data,
        )

        db.session.add(addr)

        db.session.flush()

        site = Site(name=form.name.data, address_id=addr.id, author_id=current_user.id)

        db.session.add(site)
        db.session.commit()

        return redirect(url_for("storage.site_index"))

    return render_template("storage/site/new.html", form=form)


@storage.route("/sites/view/LIMBSIT-<id>")
@login_required
def view_site(id):
    site, address, uploader = (
        db.session.query(Site, Address, User)
        .filter(Site.id == id)
        .filter(Site.author_id == User.id)
        .filter(Site.address_id == Address.id)
        .first_or_404()
    )
    rooms = db.session.query(Room).filter(Room.site_id == id).all()

    return render_template(
        "storage/site/view.html",
        site=site,
        address=address,
        rooms=rooms,
        uploader=uploader,
    )


@storage.route("/sites/view/LIMBSIT-<id>/get")
@login_required
def get_data(id):
    site = db.session.query(Site).filter(Site.id == id).first_or_404()
    rooms = db.session.query(Room).filter(Room.site_id == Site.id).all()

    output = {}

    for room in rooms:
        output[room.id] = {
            "name": room.room_number,
            "building": room.building,
            "storage": {},
        }
        fixed_storage = (
            db.session.query(FixedColdStorage)
            .filter(FixedColdStorage.room_id == room.id)
            .all()
        )
        for storage in fixed_storage:

            output[room.id]["storage"][storage.id] = {
                "serial_number": storage.serial_number,
                "manufacturer": storage.manufacturer,
                "temperature": storage.temperature.value,
                "type": storage.type.value,
                "shelves": {},
            }

            shelves = (
                db.session.query(FixedColdStorageShelf)
                .filter(FixedColdStorageShelf.storage_id == storage.id)
                .all()
            )

            for shelf in shelves:
                output[room.id]["storage"][storage.id]["shelves"][shelf.id] = {
                    "name": shelf.name,
                    "samples": {},
                    "cryo": {},
                }
                '''
                samples_to_shelf = (
                    db.session.query(SampleToFixedColdStorageShelf)
                    .filter(SampleToFixedColdStorageShelf.shelf_id == shelf.id)
                    .all()
                )

                for sample in samples_to_shelf:
                    output[room.id]["storage"][storage.id]["shelves"][shelf.id][
                        "samples"
                    ][sample.id] = {"type": sample.sample_type}

                cryo_to_shelf = (
                    db.session.query(CryovialBoxToFixedColdStorageShelf)
                    .filter(CryovialBoxToFixedColdStorageShelf.shelf_id == shelf.id)
                    .all()
                )

                for cryo in cryo_to_shelf:

                    output[room.id]["storage"][storage.id]["shelves"][shelf.id]["cryo"][
                        cryo.id
                    ] = {"test": "data"}
                '''

    return jsonify(output), 201, {"Content-Type": "application/json"}


@storage.route("/sites/room/new/LIMBSIT-<s_id>", methods=["GET", "POST"])
@login_required
def new_room(s_id):
    site = db.session.query(Site).filter(Site.id == s_id).first_or_404()

    form = RoomRegistrationForm()

    if form.validate_on_submit():
        room = Room(
            room_number=form.room.data,
            building=form.building.data,
            site_id=site.id,
            author_id=current_user.id,
        )

        db.session.add(room)
        db.session.commit()

        return redirect(url_for("storage.view_site", id=site.id))
    return render_template("storage/room/new.html", form=form, site=site)
