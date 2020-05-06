from ..models import Sample, SubSampleToSample
from ...auth.views import UserView
from ... import db


def SamplesIndexView():

    subsamples = [
        x.subsample_sample_id for x in db.session.query(SubSampleToSample).all()
    ]
    samples = db.session.query(Sample).filter(~Sample.id.in_(subsamples)).all()

    data = {}
    for sample in samples:

        data[sample.id] = {
            "sample_type": sample.sample_type.value,
            "sample_status": sample.sample_status.value,
            "creation_date": sample.creation_date,
            "user_information": UserView(sample.author_id),
        }

    return data
