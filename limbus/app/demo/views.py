from . import demo
from .. import db

from ..sample.models import Sample, SampleAttribute, SampleAttributeTextSetting, SampleAttributeOption
from ..auth.models import User
from random import randrange, choice
import datetime
import csv


def _generate_time(when: str ="before") -> str:
    current = datetime.datetime.now()
    randtime = current - datetime.timedelta(minutes=randrange(600))

    return randtime.strftime("%d/%m/%y %H:%M")

def read_csv(fp) -> list:
    with open(fp, "r") as infile:
        return list(csv.reader(infile, delimiter=","))[1:]

def _generate_user_info():
    for row in read_csv("/limbus/demo-data/user.csv"):
        user = User(
            email = row[0],
            password = "password",
            is_admin = bool(row[1])
        )

        db.session.add(user)
        db.session.commit()



def _generate_sample_data() -> None:
    users = db.session.query(User).all()
    for row in read_csv("/limbus/demo-data/sample.csv"):
        sample = Sample(
            sample_type=row[0],
            sample_status=row[3],
            collection_date=_generate_time("before"),
            disposal_instruction=row[1],
            batch_number=row[2],
            disposal_date=_generate_time("after"),
            author_id=choice(users).id
            )

        db.session.add(sample)
        db.session.commit()

def _generate_sample_attribute() -> None:
    users = db.session.query(User).all()
    for row in read_csv("/limbus/demo-data/sampleattribute.csv"):
        aid = choice(users).id
        sampleattr = SampleAttribute(
            term = row[0],
            type = row[1],
            required = False,
            author_id= aid
        )

        db.session.add(sampleattr)
        db.session.flush()

        if row[1] == "TEXT":
            setting = SampleAttributeTextSetting(
                max_length = row[2],
                sample_attribute_id=sampleattr.id
            )

            db.session.add(setting)

        if row[1] == "OPTION":
            for option in row[2].split(";"):
                attropt = SampleAttributeOption(
                    term = option,
                    author_id = aid,
                    sample_attribute_id=sampleattr.id
                )

                db.session.add(attropt)

        db.session.commit()

def _associate_sample_attributes() -> None:
    pass

@demo.route("/", methods=["GET", "POST"])
def insert_data():
    #_generate_user_info()
    #_generate_sample_data()
    #_generate_sample_attribute()
    return _generate_time()