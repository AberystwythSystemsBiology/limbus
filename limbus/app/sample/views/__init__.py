from ..models import Sample, SubSampleToSample
from ...auth.models import User
from ... import db
from ...ViewClass import ViewClass


class SamplesIndexView(ViewClass):
    """
        This class returns an dictionary of information concerning samples, as well as their author information.

        It is used in the following routes:
            - __init__.py :: index

        It is used in the following apis:
            - None.
    """
    def __init__(self):
        subsamples = [x.subsample_sample_id for x in db.session.query(SubSampleToSample).all()]
        self.samples = db.session.query(Sample, User).filter(Sample.author_id == User.id).filter(~Sample.id.in_(subsamples)).all()

    def get_attributes(self) -> dict:
        data = {}
        for sample, user in self.samples:

            data[sample.id] = {
                "sample_type" : sample.sample_type.value,
                "sample_status": sample.sample_status.value,
                "creation_date": sample.creation_date,
                "user_information" : {
                    "email": user.email,
                    "name": user.name,
                    "gravatar": user.gravatar()
                }
            }

        return data

