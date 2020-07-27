from sqlalchemy.ext.declarative import declared_attr
from app import db

class RefAuthorMixin(object):
    @declared_attr
    def author_id(cls):
        return db.Column(db.Integer, db.ForeignKey("useraccount.id"))

    @declared_attr
    def author(cls):
        return db.relationship("UserAccount",
            primaryjoin="UserAccount.id==%s.author_id" % cls.__name__
        )
