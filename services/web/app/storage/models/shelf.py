from app import db


class FixedColdStorageShelf(db.Model):
    __versioned__ = {}
    __tablename__ = "fixed_cold_storage_shelves"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String, nullable=False)

    uuid = db.Column(db.String(36))
    description = db.Column(db.String(64))

    # For ordering :)
    z_index = db.Column(db.Integer)

    storage_id = db.Column(db.Integer, db.ForeignKey("fixed_cold_storage.id"))

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
