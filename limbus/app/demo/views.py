from flask import render_template

import os
from . import demo
from .. import db

from ..auth.models import *
from ..misc.models import *
from ..patientconsentform.models import *
from ..processing.models import *
from ..sample.models import *
from ..setup.models import *
from ..storage.models import *

import pandas as pd
import numpy as np
import random

def clear_data() -> None:
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()

def from_test_data(p) -> None:
    test_df = {n: d for n, d in pd.read_excel(p, engine="odf", sheet_name=None).items()}

    for _class, _data in test_df.items():
        for _, row in _data.iterrows():
            inst = globals()[_class]()

            for attr in row.index:
                value = row[attr]
                if type(value) == np.int64:
                    value = int(value)

                setattr(inst, attr, value)

            db.session.add(inst)
            db.session.commit()

def from_priya_data(p):
    test_df = pd.read_excel(p, sheet_name="SAMPLE ENTRY", index_col=0)

    conversion_dict = {
        "Age at time of collection": 1,
        "REC NUMBER": 4,
        "Collection Group": 5,
        "Gender": 7,
        "HDBBPtCODE - HDBB00000": 6,
        "Visit Location": 2,
        "Source Material": 3,
        "Visit Location": 2,
    }

    users = db.session.query(User).all()

    for i, row in test_df.iterrows():
        sample = Sample(
            sample_type=random.choice(SampleType.choices())[0],
            collection_date=db.func.now(),
            disposal_instruction=random.choice(DisposalInstruction.choices())[0],
            disposal_date=db.func.now(),
            author_id=random.choice(users).id,
            sample_status=random.choice(SampleStatus.choices())[0],
        )

        db.session.add(sample)
        db.session.flush()

        for col_name, database_key in conversion_dict.items():

            attr = db.session.query(SampleAttribute).filter(SampleAttribute.id == database_key).first()

            row_value = row[col_name]

            if attr.type == SampleAttributeTypes.TEXT:
                if row_value == pd.np.nan:
                    row_value = "Temporary None"

                sv = SampleAttributeTextValue(
                    value = row_value,
                    sample_attribute_id = attr.id,
                    sample_id = sample.id,
                    author_id=random.choice(users).id,
                )

                db.session.add(sv)


            elif attr.type == SampleAttributeTypes.OPTION:

                sao = random.choice(db.session.query(SampleAttributeOption).all())

                saov = SampleAttributeOptionValue(
                    sample_option_id = sao.id,
                    sample_id = sample.id,
                    author_id=random.choice(users).id
                )

                db.session.add(saov)
                db.session.flush()


    db.session.commit()


@demo.route("/", methods=["GET", "POST"])
def apply_demo_data():
    demo_data_dir = "/limbus/documents/"

    clear_data()

    from_test_data(os.path.join(demo_data_dir, "testdata.ods"))
    from_priya_data(
        os.path.join(
            demo_data_dir,
            "SAFE FORMAT OF NOVEL TECHNOLOGIES SAMPLES FOR BIOBANK STORAGE 20190728 FILE.xlsx",
        )
    )

    return render_template("misc/demo.html")
