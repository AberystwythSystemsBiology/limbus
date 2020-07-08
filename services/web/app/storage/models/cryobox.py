from app import db


class SampleToCryovialBox(db.Model):
    __versioned__ = {}
    __tablename__ = "sample_to_cryovial_boxes"

    id = db.Column(db.Integer, primary_key=True)

    box_id = db.Column(db.Integer, db.ForeignKey("cryovial_boxes.id"))
    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"))

    col = db.Column(db.Integer)
    row = db.Column(db.Integer)

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))


class CryovialBoxToFixedColdStorageShelf(db.Model):
    __versioned__ = {}
    __tablename__ = "cryovial_boxes_to_fixed_cold_storage_shelf"

    id = db.Column(db.Integer, primary_key=True)

    box_id = db.Column(db.Integer, db.ForeignKey("cryovial_boxes.id"))
    shelf_id = db.Column(db.Integer, db.ForeignKey("fixed_cold_storage_shelves.id"))

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))


class CryovialBox(db.Model):
    __tablename__ = "cryovial_boxes"
    id = db.Column(db.Integer, primary_key=True)

    serial = db.Column(db.String)

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    num_rows = db.Column(db.Integer)
    num_cols = db.Column(db.Integer)

    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
