from app import db


class Site(db.Model):
    __tablename__ = "sites"
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(128))
    address_id = db.Column(db.Integer, db.ForeignKey("addresses.id"))

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
