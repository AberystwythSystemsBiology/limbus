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


def CellSampleInformationForm(cell_containers: list = [], fixation_types: list = []):
    class StaticForm(BaseTypeInformationForm):
        cell_sample_type = SelectField("Cell Sample Type", choices=CellSampleType.choices())
        tissue_sample_type = SelectField("Tissue Type", choices=TissueSampleType.choices())

    container_choices = []

    for container in cell_containers:
        container_choices.append([container["id"], "LIMBCT-%s: %s" % (container["id"], container["container"]["name"])])

    # Also, the cell container
    setattr(
        StaticForm,
        "cell_container",
        SelectField(
            "Cell Container",
            choices=container_choices,
            coerce=int
        )
    )

    fixation_type_choices = []

    for fixation in fixation_types:
        fixation_type_choices.append([fixation["id"], "LIMBCT-%s: %s" % (container["id"], container["container"]["name"])])

    setattr(
        StaticForm,
        "fixation_type",
        SelectField(
            "Fixation Type",
            choices=fixation_type_choices,
            coerce=int
        )
    )

    return StaticForm()



def MolecularSampleInformationForm(molecular_containers: list):
    class StaticForm(BaseTypeInformationForm):
        molecular_sample_type = SelectField(
            "Molecular Sample Type", choices=MolecularSampleType.choices()
        )

    choices = []

    for container in molecular_containers:
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