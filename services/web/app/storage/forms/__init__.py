# Copyright (C) 2020 Keiron O'Shea <keo7@aber.ac.uk>
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


from flask import url_for
from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SelectField,
    SelectMultipleField,
    SubmitField,
    DateField,
    TimeField,
    BooleanField,
    RadioField,
    FormField,
    FieldList,
    HiddenField,
    IntegerField,
)

from wtforms.validators import Optional
import requests
from ...misc import get_internal_api_header

import pycountry

from wtforms.validators import DataRequired, Email, EqualTo, URL, ValidationError
from ...setup.forms import post_code_validator


def func_label_sample_type(type_info: dict):
    if type_info is None or type(type_info) is not dict:
        return ""

    fluid_type = type_info.pop("fluid_type", "") or ""
    cellular_type = type_info.pop("cellular_type", "") or ""
    molecular_type = type_info.pop("molecular_type", "") or ""
    fixation_type = type_info.pop("fixation_type", None) or ""
    if fixation_type is not None and fixation_type != "":
        fixation_type = "->" + fixation_type

    sample_type = "%s %s %s %s" % (
        fluid_type,
        molecular_type,
        cellular_type,
        fixation_type,
    )
    return sample_type


def func_label_container_type(type_info: dict):
    if type_info is None or type(type_info) is not dict:
        return ""
    fluid_container = type_info.pop("fluid_container", "") or ""
    cellular_container = type_info.pop("cellular_container", "") or ""
    container_type = "%s %s" % (fluid_container, cellular_container)
    if container_type is not None and container_type != "":
        container_type = "@" + container_type
    return container_type


def func_get_samples_choices(samples: list):
    samples_choices = []
    for sample in samples:
        type_info = sample.pop("sample_type_information", "")
        sample_type = func_label_sample_type(type_info)
        container_type = func_label_container_type(type_info)
        if sample["base_type"] == "Cellular":
            metric = "Cells"
        else:
            metric = "ml"
        qty_info = "%s/%s %s" % (
            sample["remaining_quantity"],
            sample["quantity"],
            metric,
        )
        if sample["barcode"] and sample["barcode"] != "":
            sample_label = "%s: %s %s %s [%s]" % (
                sample["barcode"],
                sample_type,
                qty_info,
                container_type,
                sample["uuid"],
            )
        else:
            sample_label = "%s %s %s [%s]" % (
                sample_type,
                qty_info,
                container_type,
                sample["uuid"],
            )

        samples_choices.append([int(sample["id"]), sample_label])
    return samples_choices


class AddressForm(FlaskForm):
    address_id = HiddenField()
    country_choices = [
        (country.alpha_2, country.name) for country in pycountry.countries
    ]
    street_address_one = StringField(
        "Address Line1",
        validators=[Optional()],
        render_kw={"class": "form-control bd-light"},
    )
    street_address_two = StringField(
        "Address Line2", render_kw={"class": "form-control bd-light"}
    )
    city = StringField(
        "Town/City",
        validators=[Optional()],
        render_kw={"class": "form-control bd-light"},
    )
    county = StringField(
        "County", validators=[Optional()], render_kw={"class": "form-control bd-light"}
    )
    country = SelectField(
        "Country",
        validators=[Optional()],
        default="GB",
        choices=country_choices,
        render_kw={"class": "form-control bd-light"},
    )
    post_code = StringField(
        "Post Code",
        validators=[Optional(), post_code_validator],
        render_kw={"class": "form-control bd-light"},
    )

    is_default = BooleanField("Set as default")
    delete = BooleanField("Delete", default=True)

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        fields_required = ["street_address_one", "city", "country", "post_code"]
        success = True
        if (self.address_id.data in [None, ""]) and self.delete.data is False:
            for field in fields_required:
                value = getattr(getattr(self, field, None), "data", None)
                if value in [None, ""]:
                    err = getattr(getattr(self, field, None), "errors", None)
                    err.append("%s required." % field)
                    success = False
        return success


def SiteAddressEditForm(data={}, num_entries=None) -> FlaskForm:
    if num_entries is None or num_entries <= 0:
        num_entries = len(data["addresses"]) + 5

    class StaticForm(FlaskForm):
        name = StringField("Site Name", validators=[DataRequired()])
        url = StringField(
            "Site Website",
            validators=[URL(), Optional()],
            description="Textual string of letters with the complete http-address for the site",
        )
        description = StringField(
            "Site Description",
            description="Textual string of letters with a description about the site in English.",
        )

        num_addresses = HiddenField()

        checked = ""
        try:
            if data["is_external"]:
                checked = "checked"
        except:
            pass
        is_external = BooleanField("Is External", render_kw={"checked": checked})

        addresses = FieldList(FormField(AddressForm), min_entries=num_entries)

        submit = SubmitField("Save")

    return StaticForm(data=data)


def SiteEditForm(data={}) -> FlaskForm:
    country_choices = [
        (country.alpha_2, country.name) for country in pycountry.countries
    ]

    class StaticForm(FlaskForm):
        name = StringField("Site Name", validators=[DataRequired()])
        url = StringField(
            "Site Website",
            validators=[URL(), Optional()],
            description="Textual string of letters with the complete http-address for the site",
        )
        description = StringField(
            "Site Description",
            description="Textual string of letters with a description about the site in English.",
        )
        street_address_one = StringField("Address Line1", validators=[DataRequired()])
        street_address_two = StringField("Address Line2")
        city = StringField("Town/City", validators=[DataRequired()])
        county = StringField("County", validators=[DataRequired()])
        country = SelectField(
            "Country",
            validators=[DataRequired()],
            default="GB",
            choices=country_choices,
        )
        post_code = StringField(
            "Post Code", validators=[DataRequired(), post_code_validator]
        )

        checked = ""
        try:
            if data["is_external"]:
                checked = "checked"
        except:
            pass

        is_external = BooleanField("Is External", render_kw={"checked": checked})
        submit = SubmitField("Save")

    return StaticForm(data=data)


def SampleToEntityForm(samples: list) -> FlaskForm:
    samples_choices = func_get_samples_choices(samples)
    samples_choices.insert(0, [0, "--- Select a samples ---"])

    class StaticForm(FlaskForm):

        date = DateField(
            "Entry Date", validators=[DataRequired()], default=datetime.today()
        )
        time = TimeField(
            "Entry Time", validators=[DataRequired()], default=datetime.now()
        )
        entered_by = StringField(
            "Entered By",
            description="The initials of the person that entered the sample.",
            validators=[DataRequired()],
        )

        submit = SubmitField("Submit")

    setattr(
        StaticForm,
        "samples",
        SelectField(
            "Sample",
            choices=samples_choices,
            validators=[DataRequired()],
            coerce=int,
            # render_kw={'onchange': "check_sample()"}
        ),
    )

    return StaticForm()


def SamplesToEntityForm(samples: list) -> FlaskForm:
    samples_choices = func_get_samples_choices(samples)
    samples_choices.insert(0, [0, "--- Select at least one samples ---"])

    class StaticForm(FlaskForm):
        date = DateField(
            "Entry Date", validators=[DataRequired()], default=datetime.today()
        )
        time = TimeField(
            "Entry Time", validators=[DataRequired()], default=datetime.now()
        )
        entered_by = StringField(
            "Entered By",
            description="The initials of the person that entered the sample.",
            validators=[DataRequired()],
        )
        checked = "checked"
        fillopt_column_first = BooleanField(
            "Column first (uncheck for row first)", render_kw={"checked": checked}
        )
        fillopt_skip_gaps = BooleanField("Skip gaps", render_kw={"checked": checked})

        submit = SubmitField("Submit")

    default_choices = [int(s[0]) for s in samples_choices if int(s[0]) > 0]

    setattr(
        StaticForm,
        "samples",
        SelectMultipleField(
            "Sample(s)",
            choices=samples_choices,
            default=default_choices,
            validators=[DataRequired()],
            coerce=int,
            # render_kw={'multiple': True},#render_kw={'onchange': "check_sample()"}
        ),
    )

    return StaticForm()


from .building import *
from .lts import *
from .rack import *
from .room import *
from .shelf import *
