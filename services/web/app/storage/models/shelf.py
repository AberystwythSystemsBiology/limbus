from app import db


class FixedColdStorageShelf(db.Model):
    __tablename__ = "fixed_cold_storage_shelves"
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String, nullable=False)
    storage_id = db.Column(db.Integer, db.ForeignKey("fixed_cold_storage.id"))

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))


class SampleToFixedColdStorageShelf(db.Model):
    __tablename__ = "sample_to_fixed_cold_storage_shelf"
    id = db.Column(db.Integer, primary_key=True)

    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"))
    shelf_id = db.Column(db.Integer, db.ForeignKey("fixed_cold_storage_shelves.id"))

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
