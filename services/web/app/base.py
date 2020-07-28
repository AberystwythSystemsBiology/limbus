from sqlalchemy.ext.declarative import as_declarative, declared_attr
from app import db


@as_declarative()
class BaseModel(object):

    id = db.Column(db.Integer, primary_key=True)

    created_on = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    updated_on = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )