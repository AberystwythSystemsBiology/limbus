# Copyright (C) 2020 Keiron O'Shea <keo7@aber.ac.uk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as p7ublished by
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

from ...enums import (
    BiohazardLevel,
    TissueSampleType,
    FluidSampleType,
    MolecularSampleType,
    CellSampleType,

)

from wtforms import SelectField, FloatField, SubmitField

from wtforms.validators import DataRequired, Optional


class BaseTypeInformationForm(FlaskForm):

    biohazard_level = SelectField(
        "Biohazard Level",
        choices=BiohazardLevel.choices(),
        description="BSL category for the sample.",
    )

    quantity = FloatField("Quantity", validators=[DataRequired()])

    submit = SubmitField("Continue")


def FluidSampleInformationForm(fluid_containers: list = []):

    class StaticForm(BaseTypeInformationForm):
        fluid_sample_type = SelectField(
            "Fluid Sample Type", choices=FluidSampleType.choices()
        )

    choices = []

    for container in fluid_containers:
        choices.append([container["id"], "LIMBCT-%s: %s" % (container["id"], container["container"]["name"])])

    setattr(
        StaticForm,
        "fluid_container",
        SelectField(
            "Fluid Container",
            choices=choices,
            coerce=int
        )
    )

    return StaticForm()


class CellSampleInformationForm(BaseTypeInformationForm):
    cell_sample_type = SelectField("Cell Sample Type", choices=CellSampleType.choices())
    tissue_sample_type = SelectField("Tissue Type", choices=TissueSampleType.choices())
    # Also, the fixation type
    # Also, the cell container

class MolecularSampleInformationForm(BaseTypeInformationForm):
    # Also, the fluid container.
    molecular_sample_type = SelectField(
        "Molecular Sample Type", choices=MolecularSampleType.choices()
    )

