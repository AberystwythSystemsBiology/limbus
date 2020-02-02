from . import demo
from .. import db

from ..sample.models import Sample, SampleAttribute, SampleAttributeTextSetting,\
    SampleAttributeOption, SampleAttributeOptionValue, SampleAttributeTextValue
from ..sample.enums import SampleAttributeTypes
from ..auth.models import User
from random import randrange, choice
import datetime
import csv



def _generate_time(before: bool = True) -> str:
    current = datetime.datetime.now()
    '''
    if before:
        randtime = current - datetime.timedelta(minutes=randrange(6000))
    else:
        randtime = current + datetime.timedelta(minutes=randrange(6000))
    '''

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
            collection_date=_generate_time(True),
            disposal_instruction=row[1],
            batch_number=row[2],
            disposal_date=_generate_time(False),
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
    sample_attributes = db.session.query(SampleAttribute).all()
    samples = db.session.query(Sample).all()
    users = db.session.query(User).all()

    for i in range(75):
        sample_attr = choice(sample_attributes)
        sample_choice = choice(samples)


        if sample_attr.type == SampleAttributeTypes.OPTION:
            sample_attr_opts = db.session.query(SampleAttributeOption).filter(
                SampleAttributeOption.sample_attribute_id == sample_attr.id
            ).all()

            sample_opt = choice(sample_attr_opts)

            if len(db.session.query(SampleAttributeOptionValue, SampleAttributeOption).filter(
                    SampleAttributeOptionValue.sample_id == sample_choice.id
            ).filter(
                SampleAttributeOptionValue.sample_attribute_id == sample_attr.id
            ).all()) == 0:
                sao = SampleAttributeOptionValue(
                    sample_option_id = sample_opt.id,
                    sample_attribute_id = sample_attr.id,
                    sample_id = sample_choice.id,
                    author_id = choice(users).id,
                )

                db.session.add(sao)
                db.session.commit()

        elif sample_attr.type == SampleAttributeTypes.TEXT:

            if len(db.session.query(SampleAttributeTextValue).filter(
                    SampleAttributeTextValue.sample_id == sample_choice.id
            ).filter(
                SampleAttributeTextValue.sample_attribute_id == sample_attr.id
            ).all()) == 0:

                sat = SampleAttributeTextValue(
                    value = "Random text",
                    sample_attribute_id = sample_attr.id,
                    sample_id = sample_choice.id,
                    author_id = choice(users).id
                )

                db.session.add(sat)
                db.session.commit()


@demo.route("/", methods=["GET", "POST"])
def insert_data():
    _generate_user_info()
    _generate_sample_data()
    _generate_sample_attribute()
    _associate_sample_attributes()

    return _generate_time()