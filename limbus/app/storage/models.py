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

class ColdStorage(db.Model):
    __tablename__ = "cold_storage"

    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.String)
    manufacturer = db.Column(db.String)

    temperature = db.Column(db.String)
    num_shelves = db.Column(db.Integer, nullable=False)
    # Enumerated type for freezer/fridge.
    #type = db.Column(db.Enum())

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    site_id = db.Column(db.Integer, db.ForeignKey("sites.id"))

    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

class DataPaqRack(db.Model):
    __tablename__ = "data_paq_rack"
    id = db.Column(db.Integer, primary_key=True)

    pass

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
