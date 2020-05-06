from app import db
from ..enums import *

class SampleToFluidSampleType(db.Model):
    __tablename__ = "sample_to_fluid_sample_types"

    id = db.Column(db.Integer, primary_key=True)

    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"))
    sample_type = db.Column(db.Enum(FluidSampleType))

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

class SampleToMolecularSampleType(db.Model):
    __tablename__ = "sample_to_molecular_sample_types"

    id = db.Column(db.Integer, primary_key=True)

    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"))
    sample_type = db.Column(db.Enum(MolecularSampleType))

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))


class SampleToCellSampleType(db.Model):
    __tablename__ = "sample_to_cell_sample_types"

    id = db.Column(db.Integer, primary_key=True)

    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"))
    sample_type = db.Column(db.Enum(CellSampleType))

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))


class SampleToTissueSampleType(db.Model):
    __tablename__ = "sample_to_tissue_sample_types"

    id = db.Column(db.Integer, primary_key=True)

    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"))
    sample_type = db.Column(db.Enum(TissueSampleType))

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))


