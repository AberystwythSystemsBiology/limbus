from app import db


class Room(db.Model):
    __tablename__ = "rooms"
    id = db.Column(db.Integer, primary_key=True)

    room_number = db.Column(db.String(256), nullable=False)
    building = db.Column(db.String(128))

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    site_id = db.Column(db.Integer, db.ForeignKey("sites.id"))

    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
