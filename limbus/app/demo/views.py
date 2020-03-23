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

demo_data_dir = "/limbus/data/"

@demo.route("/", methods=["GET", "POST"])
def apply_demo_data():
    pass