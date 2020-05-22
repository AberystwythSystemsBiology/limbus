from .. import db
from .models import DiagnosticProcedureClass, DiagnosticProcedureVolume, DiagnosticProcedureSubheading, DiagnosticProcedure
from ..auth.views import UserView

def DiagnosticProceduresIndexView() -> dict:
    data = {}

    for procedure in db.session.query(DiagnosticProcedureClass).all():
        data[procedure.id] = {
            "name": procedure.name,
            "version": procedure.version,
            "upload_date": procedure.creation_date,
            "update_date": procedure.update_date,
            "user_information": UserView(procedure.author_id),
        }

    return data

def DiagnosticProcedureView(proc_id) -> dict:
    proc = db.session.query(DiagnosticProcedureClass).filter(DiagnosticProcedureClass.id == proc_id).first_or_404()

    volumes = db.session.query(DiagnosticProcedureVolume).filter(DiagnosticProcedureVolume.class_id == proc_id).all()

    data = {
        "id": proc.id,
        "name": proc.name,
        "version": proc.version,
        "upload_date": proc.creation_date,
        "update_date": proc.update_date,
        "user_information": UserView(proc.author_id),
        "volumes" : {}
    }

    for volume in volumes:
        data["volumes"][volume.id] = {
            "code" : volume.code,
            "name" : volume.name,
            "subheadings": {}
        }

        subheadings = db.session.query(DiagnosticProcedureSubheading).filter(DiagnosticProcedureSubheading.volume_id == volume.id).all()

        for sh in subheadings:


            diagnostic_procs = db.session.query(DiagnosticProcedure).filter(DiagnosticProcedure.subheading_id == sh.id).all()

            codes = {}

            for proc in diagnostic_procs:
                codes[proc.id] = {
                    "code": proc.code,
                    "procedure": proc.procedure
                }

            data["volumes"][volume.id]["subheadings"][sh.id] = {
                "code": sh.code,
                "subheading": sh.subheading,
                "codes": codes
            }

            


    return data

