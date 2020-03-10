from flask import redirect, abort, render_template, url_for, session, request, jsonify

from flask_login import current_user
from ... import db
from .. import storage

from ..forms import SiteRegistrationForm, RoomRegistrationForm

from ..models import Site, Room

from ...misc.models import Address
from ...auth.models import User


@storage.route("sites/")
def site_index():
    sites = db.session.query(Site, User).filter(Site.author_id == User.id).all()
    return render_template("storage/site/index.html", sites=sites)


@storage.route("sites/new", methods=["GET", "POST"])
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


@storage.route("/sites/room/new/LIMBSIT-<s_id>", methods=["GET", "POST"])
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
