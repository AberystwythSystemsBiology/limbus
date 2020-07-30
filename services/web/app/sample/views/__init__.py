# Copyright (C) 2019  Keiron O'Shea <keo7@aber.ac.uk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from ..models import Sample, SubSampleToSample
from ...auth.views import UserView
from ... import db
from .sample import BasicSampleView, SampleView


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
