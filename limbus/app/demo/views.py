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

def clear_data():
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()

def from_test_data(p):
    test_df = {n: d for n, d in pd.read_excel(p, engine="odf", sheet_name=None).items()}

    clear_data()

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


@demo.route("/", methods=["GET", "POST"])
def apply_demo_data():
    demo_data_dir = "/limbus/documents/"
    test_data_path = os.path.join(demo_data_dir, "testdata.ods")

    from_test_data(test_data_path)
