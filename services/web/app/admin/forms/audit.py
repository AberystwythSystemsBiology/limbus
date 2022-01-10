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

from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, BooleanField, SelectMultipleField, DateField
from datetime import datetime
from ..enums import *

def AuditFilterForm(sites: list, users: list, data={}) -> FlaskForm:
    users.insert(0, (0, "None"))
    sites.insert(0, (0, "None"))

    class StaticForm(FlaskForm):
        start_date = DateField(
            "Start Date",
            default=datetime.today(),
        )
        end_date = DateField(
            "End Date",
            default=datetime.today(),
        )

        audit_type = SelectField(
            "Audit Type", choices=AuditTypes.choices(with_none=False),
        )

        general_object = SelectMultipleField(
            "General Objects", choices=GeneralObject.choices(),#with_none=True),
            default=[k[0] for k in GeneralObject.choices()],
        )
        sample_object = SelectMultipleField(
            "Sample Objects", choices=SampleObject.choices(),#with_none=False),
            default=[k[0] for k in SampleObject.choices()],
        )

        donor_object = SelectMultipleField(
            "Donor Objects", choices=DonorObject.choices(), #with_none=False),
            default=[k[0] for k in DonorObject.choices()],
        )

        template_object = SelectMultipleField(
            "SOP Objects", choices=TemplateObject.choices(), #with_none=False),
            default=[k[0] for k in TemplateObject.choices()],
        )
        storage_object = SelectMultipleField(
            "Cold Storage", choices=StorageObject.choices(), #with_none=False),
            default=[k[0] for k in StorageObject.choices()],
        )
        auth_object = SelectMultipleField(
            "User & Sites", choices=AuthObject.choices(), #with_none=False),
            default=[k[0] for k in AuthObject.choices()],
        )

        site_id = SelectField("User Affiliated Site", choices=sites, default=None)
        user_id = SelectField("User", choices=users, default=None)
        uuid = StringField("Object UUID")

        submit = SubmitField("Filter")

    return StaticForm()