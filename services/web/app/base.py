from . import Base, db
from sqlalchemy.ext.declarative import declared_attr

class RefAuthorMixin(object):
    @declared_attr
    def author_id(cls):
        return db.Column(db.Integer, db.ForeignKey('useraccount.id'))

    @declared_attr
    def author(cls):
        return db.relationship("UserAccount")

class BasicModel(object):
    __versioned__ = {}

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = db.Column(db.Integer, primary_key=True)

    created_on = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_on = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )