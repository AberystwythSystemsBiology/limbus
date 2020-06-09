from app import db

class DiagnosticProcedureClass(db.Model):
    __versioned__ = {}
    __tablename__ = "diagnostic_procedure_classes"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String)
    version = db.Column(db.String)
    description = db.Column(db.String)

    
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    updater_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

class DiagnosticProcedureVolume(db.Model):
    __versioned__ = {}
    __tablename__ = "diagnostic_procedure_volumes"

    id = db.Column(db.Integer, primary_key=True)

    code = db.Column(db.String(5))
    name = db.Column(db.String)

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    updater_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    class_id = db.Column(db.Integer, db.ForeignKey("diagnostic_procedure_classes.id"))

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

class DiagnosticProcedureSubheading(db.Model):
    __versioned__ = {}
    __tablename__ = "diagnostic_procedure_subheadings"

    id = db.Column(db.Integer, primary_key=True)

    code = db.Column(db.String(5))
    subheading = db.Column(db.String())

    # Website linking to page?
    reference = db.Column(db.String(256))

    volume_id = db.Column(db.Integer, db.ForeignKey("diagnostic_procedure_volumes.id"))

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    updater_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

class DiagnosticProcedure(db.Model):
    __versioned__ = {}
    __tablename__ = "diagnostic_procedures"

    id = db.Column(db.Integer, primary_key=True)

    code = db.Column(db.String(5))
    procedure = db.Column(db.String())

    # Website linking to page?
    reference = db.Column(db.String(256))

    subheading_id = db.Column(db.Integer, db.ForeignKey("diagnostic_procedure_subheadings.id"))

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    updater_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )