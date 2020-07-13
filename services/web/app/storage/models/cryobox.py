from app import db


class CryovialBox(db.Model):
    __tablename__ = "cryovial_boxes"
    id = db.Column(db.Integer, primary_key=True)

    serial = db.Column(db.String)

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    removed = db.Column(db.Boolean)

    num_rows = db.Column(db.Integer)
    num_cols = db.Column(db.Integer)

    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
