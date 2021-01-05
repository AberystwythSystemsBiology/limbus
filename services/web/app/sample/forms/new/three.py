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
    SampleBaseType,
    TissueSampleType,
    FluidSampleType,
    MolecularSampleType,
    CellSampleType,
    FixationType,
    CellContainer,
    FluidContainer
)

from wtforms import (
    SelectField,
    FloatField,
    SubmitField
)

from wtforms.validators import DataRequired, Optional



class SampleTypeSelectForm(FlaskForm):

    biohazard_level = SelectField(
        "Biohazard Level",
        choices=BiohazardLevel.choices(),
        description="BSL category for the sample.",
    )

    sample_type = SelectField("Sample Type", choices=SampleBaseType.choices())
    fluid_sample_type = SelectField(
        "Fluid Sample Type", choices=FluidSampleType.choices()
    )

    tissue_sample_type = SelectField("Tissue Type", choices=TissueSampleType.choices())

    molecular_sample_type = SelectField(
        "Molecular Sample Type", choices=MolecularSampleType.choices()
    )
    cell_sample_type = SelectField("Cell Sample Type", choices=CellSampleType.choices())

    quantity = FloatField("Quantity", validators=[DataRequired()])
    fixation_type = SelectField("Fixation Type", choices=FixationType.choices())

    fluid_container = SelectField("Fluid Container", choices=FluidContainer.choices())
    cell_container = SelectField("Cell Container", choices=CellContainer.choices())

    submit = SubmitField("Continue")
