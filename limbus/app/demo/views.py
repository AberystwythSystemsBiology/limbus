from . import demo
from .. import db

from ..sample.models import Sample
from random import randrange
import datetime
import csv

@demo.route("/", methods=["GET", "POST"])
def insert_data():


    def _generate_time():
        current = datetime.datetime.now()
        randtime = current + datetime.timedelta(minutes=randrange(60))
        return randtime.strftime("%d/%m/%y %H:%M")


    [_generate_time() for x in range(10)]
    with open("/limbus/demo-data/sample.csv", "r") as infile:
        csv_reader = list(csv.reader(infile, delimiter=","))

        for row in csv_reader[1:]:
            sample = Sample(
                id=row[0],
                sample_type=row[1],
                sample_status=row[5],
                collection_date=_generate_time(),
                disposal_instruction=row[3],
                batch_number=row[4],
                disposal_date=_generate_time(),
                author_id=1
            )

            db.session.add(sample)
            db.session.commit()

    return "Data Entered"