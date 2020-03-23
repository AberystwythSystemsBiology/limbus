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
from datetime import datetime, timedelta


def gen_datetime(min_year=2018, max_year=2050):
    # generate a datetime in format yyyy-mm-dd hh:mm:ss.000000
    start = datetime(min_year, 1, 1, 00, 00, 00)
    years = max_year - min_year + 1
    end = start + timedelta(days=365 * years)
    return start + (end - start) * random.random()


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

    custom_attr = {
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
        )
        db.session.add(sample)

        db.session.flush()

        for key in custom_attr.keys():
            attr_value = (
                db.session.query(SampleAttribute)
                .filter(SampleAttribute.id == custom_attr[key])
                .first()
            )

            if attr_value.type == SampleAttributeTypes.TEXT:
                sv = SampleAttributeTextValue(
                    sample_id=sample.id,
                    sample_attribute_id=attr_value.id,
                    value=row[key],
                )

            elif attr_value.type == SampleAttributeTypes.OPTION:
                _l = (
                    db.session.query(SampleAttributeOption)
                    .filter(SampleAttributeOption.term == row[key])
                    .first()
                )

                print(_l)

            db.session.add(sv)

            print(key, row[key], attr_value)

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

    return "<h1>DATA APPLIED, GO AWAY</h1>"
